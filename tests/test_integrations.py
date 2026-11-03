from tests import app, client, auth_headers


def test_preview_and_commit_client_import(client, auth_headers):
    preview = client.post('/integrations/imports/clients/preview', json={'rows': [
        {'name': 'Imported One', 'age': 31, 'email': 'one@example.com'},
        {'name': '', 'age': 200}
    ]}, headers=auth_headers)
    assert preview.status_code == 200
    assert preview.get_json()['total'] == 2
    assert preview.get_json()['invalid'] == 1

    committed = client.post('/integrations/imports/clients/commit', json={'rows': [
        {'name': 'Imported Two', 'age': 40}
    ]}, headers={**auth_headers, 'Idempotency-Key': 'import-test-one'})
    assert committed.status_code == 201

    replay = client.post('/integrations/imports/clients/commit', json={'rows': [
        {'name': 'Imported Two', 'age': 40}
    ]}, headers={**auth_headers, 'Idempotency-Key': 'import-test-one'})
    assert replay.status_code == 201
    assert replay.get_json()['created'] == 1


def test_create_and_revoke_api_credential(client, auth_headers):
    created = client.post('/integrations/credentials', json={'name': 'Production API'}, headers=auth_headers)
    assert created.status_code == 201
    assert created.get_json()['api_key'].startswith('his_')

    credential_id = created.get_json()['id']
    revoked = client.post(f'/integrations/credentials/{credential_id}/revoke', headers=auth_headers)
    assert revoked.status_code == 200
    assert revoked.get_json()['status'] == 'revoked'


def test_create_webhook_and_delivery(client, auth_headers):
    webhook = client.post('/integrations/webhooks', json={
        'name': 'Operations receiver',
        'url': 'https://example.com/health-events'
    }, headers=auth_headers)
    assert webhook.status_code == 201
    assert webhook.get_json()['signing_secret']

    endpoint_id = webhook.get_json()['id']
    delivery = client.post(f'/integrations/webhooks/{endpoint_id}/deliveries', json={
        'event_type': 'client.created',
        'payload': {'client_id': 'test-client-id'}
    }, headers=auth_headers)
    assert delivery.status_code == 201
    assert delivery.get_json()['status'] == 'pending'


def test_rejected_import_is_not_committed(client, auth_headers):
    response = client.post('/integrations/imports/clients/commit', json={'rows': [
        {'name': '', 'age': 'invalid'}
    ]}, headers={**auth_headers, 'Idempotency-Key': 'rejected-import-test'})
    assert response.status_code == 409


def test_import_commit_requires_idempotency_key(client, auth_headers):
    response = client.post('/integrations/imports/clients/commit', json={'rows': [
        {'name': 'No Idempotency Key', 'age': 30}
    ]}, headers=auth_headers)
    assert response.status_code == 400


def test_idempotency_key_rejects_different_payload(client, auth_headers):
    headers = {**auth_headers, 'Idempotency-Key': 'payload-bound-key'}
    first = client.post('/integrations/imports/clients/commit', json={'rows': [
        {'name': 'Payload A', 'age': 30}
    ]}, headers=headers)
    assert first.status_code == 201

    different = client.post('/integrations/imports/clients/commit', json={'rows': [
        {'name': 'Payload B', 'age': 31}
    ]}, headers=headers)
    assert different.status_code == 409

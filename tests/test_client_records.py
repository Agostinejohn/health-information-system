from tests import app, client, auth_headers, doctor_headers


def test_register_client_with_extended_fields(client, doctor_headers):
    response = client.post('/clients', json={
        'name': 'Extended Client',
        'age': 29,
        'external_reference': 'EXT-1001',
        'email': 'extended@example.com',
        'phone': '+254700000001',
        'address': 'Nairobi'
    }, headers=doctor_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['email'] == 'extended@example.com'
    assert data['phone'] == '+254700000001'
    assert data['status'] == 'active'


def test_duplicate_client_is_blocked(client, doctor_headers):
    payload = {'name': 'Duplicate Person', 'age': 35, 'phone': '+254700000002'}
    first = client.post('/clients', json=payload, headers=doctor_headers)
    assert first.status_code == 201

    response = client.post('/clients', json=payload, headers=doctor_headers)
    assert response.status_code == 409
    assert response.get_json()['error'] == 'Possible duplicate client found'


def test_client_consent_document_and_timeline(client, doctor_headers):
    created = client.post('/clients', json={'name': 'Clinical Timeline', 'age': 42}, headers=doctor_headers)
    client_id = created.get_json()['id']

    consent = client.post(f'/clients/{client_id}/consents', json={
        'consent_type': 'data_processing',
        'granted': True,
        'note': 'Recorded verbally'
    }, headers=doctor_headers)
    assert consent.status_code == 201

    document = client.post(f'/clients/{client_id}/documents', json={
        'title': 'Referral letter',
        'category': 'referral',
        'storage_key': 'organizations/demo/clients/referral.pdf',
        'content_type': 'application/pdf'
    }, headers=doctor_headers)
    assert document.status_code == 201

    timeline = client.get(f'/clients/{client_id}/timeline', headers=doctor_headers)
    assert timeline.status_code == 200
    assert timeline.get_json()[0]['event_type'] == 'registration'

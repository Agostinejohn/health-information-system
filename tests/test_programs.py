from tests import app, client, auth_headers, doctor_headers

def test_create_program_as_admin(client, auth_headers):
    res = client.post('/programs', json={'name': 'TB'}, headers=auth_headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data['name'] == 'TB'
    assert 'id' in data

def test_create_program_as_doctor_forbidden(client, doctor_headers):
    res = client.post('/programs', json={'name': 'HIV'}, headers=doctor_headers)
    assert res.status_code == 403

def test_create_program_duplicate(client, auth_headers):
    client.post('/programs', json={'name': 'Malaria'}, headers=auth_headers)
    res = client.post('/programs', json={'name': 'Malaria'}, headers=auth_headers)
    assert res.status_code == 409

def test_create_program_missing_name(client, auth_headers):
    res = client.post('/programs', json={}, headers=auth_headers)
    assert res.status_code == 400
    assert 'errors' in res.get_json()

def test_create_program_empty_name(client, auth_headers):
    res = client.post('/programs', json={'name': ''}, headers=auth_headers)
    assert res.status_code == 400

def test_list_programs(client, auth_headers):
    client.post('/programs', json={'name': 'TB'}, headers=auth_headers)
    client.post('/programs', json={'name': 'HIV'}, headers=auth_headers)
    res = client.get('/programs', headers=auth_headers)
    assert res.status_code == 200
    assert len(res.get_json()) == 2

def test_list_programs_empty(client, auth_headers):
    res = client.get('/programs', headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json() == []

def test_list_programs_no_token(client):
    res = client.get('/programs')
    assert res.status_code == 401

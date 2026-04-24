from tests import app, client, auth_headers, doctor_headers

def test_register_client(client, doctor_headers):
    res = client.post('/clients', json={'name': 'Jane Doe', 'age': 28}, headers=doctor_headers)
    assert res.status_code == 201
    data = res.get_json()
    assert data['name'] == 'Jane Doe'
    assert data['age'] == 28
    assert 'id' in data

def test_register_client_missing_name(client, doctor_headers):
    res = client.post('/clients', json={'age': 28}, headers=doctor_headers)
    assert res.status_code == 400
    assert 'errors' in res.get_json()

def test_register_client_missing_age(client, doctor_headers):
    res = client.post('/clients', json={'name': 'John'}, headers=doctor_headers)
    assert res.status_code == 400

def test_register_client_invalid_age(client, doctor_headers):
    res = client.post('/clients', json={'name': 'John', 'age': -5}, headers=doctor_headers)
    assert res.status_code == 400

def test_register_client_age_too_high(client, doctor_headers):
    res = client.post('/clients', json={'name': 'John', 'age': 200}, headers=doctor_headers)
    assert res.status_code == 400

def test_search_clients(client, doctor_headers):
    client.post('/clients', json={'name': 'Alice Wanjiku', 'age': 30}, headers=doctor_headers)
    client.post('/clients', json={'name': 'Bob Kamau', 'age': 25}, headers=doctor_headers)
    res = client.get('/clients?name=Alice', headers=doctor_headers)
    assert res.status_code == 200
    results = res.get_json()
    assert len(results) == 1
    assert results[0]['name'] == 'Alice Wanjiku'

def test_search_clients_no_param(client, doctor_headers):
    res = client.get('/clients', headers=doctor_headers)
    assert res.status_code == 400

def test_search_clients_no_match(client, doctor_headers):
    res = client.get('/clients?name=Zzzzz', headers=doctor_headers)
    assert res.status_code == 200
    assert res.get_json() == []

def test_get_client_profile(client, doctor_headers):
    res = client.post('/clients', json={'name': 'Mary Auma', 'age': 34}, headers=doctor_headers)
    client_id = res.get_json()['id']
    res = client.get(f'/clients/{client_id}', headers=doctor_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data['name'] == 'Mary Auma'
    assert 'programs' in data

def test_get_client_not_found(client, doctor_headers):
    res = client.get('/clients/nonexistent-id', headers=doctor_headers)
    assert res.status_code == 404

def test_enroll_client_in_program(client, auth_headers, doctor_headers):
    prog_res = client.post('/programs', json={'name': 'TB'}, headers=auth_headers)
    program_id = prog_res.get_json()['id']

    client_res = client.post('/clients', json={'name': 'Peter Otieno', 'age': 40}, headers=doctor_headers)
    client_id = client_res.get_json()['id']

    res = client.post(f'/clients/{client_id}/enroll',
                      json={'program_ids': [program_id]},
                      headers=doctor_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['client']['programs']) == 1
    assert data['client']['programs'][0]['name'] == 'TB'
    assert 'TB' in data['enrollment_result']['enrolled']

def test_enroll_nonexistent_client(client, auth_headers, doctor_headers):
    prog_res = client.post('/programs', json={'name': 'HIV'}, headers=auth_headers)
    program_id = prog_res.get_json()['id']
    res = client.post('/clients/fake-id/enroll',
                      json={'program_ids': [program_id]},
                      headers=doctor_headers)
    assert res.status_code == 404

def test_enroll_nonexistent_program(client, doctor_headers):
    client_res = client.post('/clients', json={'name': 'Grace Njeri', 'age': 22}, headers=doctor_headers)
    client_id = client_res.get_json()['id']
    res = client.post(f'/clients/{client_id}/enroll',
                      json={'program_ids': ['fake-program-id']},
                      headers=doctor_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert 'fake-program-id' in data['enrollment_result']['not_found']

def test_enroll_duplicate_ignored(client, auth_headers, doctor_headers):
    prog_res = client.post('/programs', json={'name': 'Malaria'}, headers=auth_headers)
    program_id = prog_res.get_json()['id']
    client_res = client.post('/clients', json={'name': 'Sam Odhiambo', 'age': 31}, headers=doctor_headers)
    client_id = client_res.get_json()['id']

    client.post(f'/clients/{client_id}/enroll', json={'program_ids': [program_id]}, headers=doctor_headers)
    res = client.post(f'/clients/{client_id}/enroll', json={'program_ids': [program_id]}, headers=doctor_headers)
    assert res.status_code == 200
    assert len(res.get_json()['client']['programs']) == 1

def test_enroll_missing_program_ids(client, doctor_headers):
    client_res = client.post('/clients', json={'name': 'Test User', 'age': 25}, headers=doctor_headers)
    client_id = client_res.get_json()['id']
    res = client.post(f'/clients/{client_id}/enroll', json={}, headers=doctor_headers)
    assert res.status_code == 400

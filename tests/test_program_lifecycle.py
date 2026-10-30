from tests import app, client, auth_headers, doctor_headers


def test_create_configured_program(client, auth_headers):
    response = client.post('/programs', json={
        'name': 'Maternal Care',
        'description': 'Prenatal and postnatal support',
        'status': 'active',
        'capacity': 25,
        'start_date': '2026-10-01'
    }, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['capacity'] == 25
    assert data['start_date'] == '2026-10-01'


def test_update_program_status(client, auth_headers):
    created = client.post('/programs', json={'name': 'Screening Program'}, headers=auth_headers)
    program_id = created.get_json()['id']

    response = client.patch(f'/programs/{program_id}', json={
        'status': 'paused',
        'capacity': 10
    }, headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()['status'] == 'paused'
    assert response.get_json()['capacity'] == 10


def test_lifecycle_enrollment_and_status_update(client, auth_headers, doctor_headers):
    program = client.post('/programs', json={'name': 'Nutrition', 'capacity': 5}, headers=auth_headers).get_json()
    registered = client.post('/clients', json={'name': 'Program Client', 'age': 28}, headers=doctor_headers).get_json()

    enrolled = client.post(f"/clients/{registered['id']}/enroll", json={
        'program_ids': [program['id']]
    }, headers=doctor_headers)
    assert enrolled.status_code == 200
    assert 'Nutrition' in enrolled.get_json()['enrollment_result']['enrolled']

    status = client.patch(
        f"/clients/{registered['id']}/enrollments/{program['id']}",
        json={'status': 'completed', 'reason': 'Programme target achieved'},
        headers=auth_headers
    )
    assert status.status_code == 200
    assert status.get_json()['status'] == 'completed'

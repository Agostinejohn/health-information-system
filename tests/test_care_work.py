from tests import app, client, auth_headers, doctor_headers


def test_create_and_complete_appointment(client, auth_headers, doctor_headers):
    registered = client.post('/clients', json={'name': 'Appointment Client', 'age': 36}, headers=doctor_headers).get_json()
    created = client.post('/appointments', json={
        'client_id': registered['id'],
        'scheduled_at': '2026-11-10T09:30:00',
        'timezone': 'Africa/Nairobi',
        'reason': 'Routine review'
    }, headers=doctor_headers)
    assert created.status_code == 201
    appointment_id = created.get_json()['id']

    updated = client.patch(f'/appointments/{appointment_id}', json={
        'status': 'completed',
        'notes': 'Review completed'
    }, headers=doctor_headers)
    assert updated.status_code == 200
    assert updated.get_json()['status'] == 'completed'

    listed = client.get('/appointments', headers=doctor_headers)
    assert listed.status_code == 200
    assert listed.get_json()[0]['client_id'] == registered['id']


def test_create_and_complete_follow_up(client, doctor_headers):
    registered = client.post('/clients', json={'name': 'Follow Up Client', 'age': 41}, headers=doctor_headers).get_json()
    created = client.post('/follow-ups', json={
        'client_id': registered['id'],
        'due_at': '2026-11-12T10:00:00',
        'priority': 'high',
        'title': 'Confirm treatment adherence'
    }, headers=doctor_headers)
    assert created.status_code == 201

    updated = client.patch(f"/follow-ups/{created.get_json()['id']}", json={
        'status': 'completed'
    }, headers=doctor_headers)
    assert updated.status_code == 200
    assert updated.get_json()['completed_at']


def test_create_and_complete_referral(client, doctor_headers):
    registered = client.post('/clients', json={'name': 'Referral Client', 'age': 52}, headers=doctor_headers).get_json()
    created = client.post('/referrals', json={
        'client_id': registered['id'],
        'destination': 'City Diagnostic Centre',
        'reason': 'Specialist diagnostic assessment',
        'priority': 'high'
    }, headers=doctor_headers)
    assert created.status_code == 201

    updated = client.patch(f"/referrals/{created.get_json()['id']}", json={
        'status': 'completed',
        'outcome': 'Assessment accepted and appointment scheduled'
    }, headers=doctor_headers)
    assert updated.status_code == 200
    assert updated.get_json()['status'] == 'completed'
    assert updated.get_json()['outcome_at']


def test_care_work_blocks_cross_tenant_client(client, auth_headers, doctor_headers):
    other_org = client.post('/organizations', json={'name': 'Other Care Organisation'}, headers={
        'Authorization': doctor_headers['Authorization']
    }).get_json()

    created = client.post('/appointments', json={
        'client_id': 'unknown-cross-tenant-client',
        'scheduled_at': '2026-11-10T09:30:00'
    }, headers=doctor_headers)
    assert created.status_code == 404

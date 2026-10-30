from tests import app, client, auth_headers, doctor_headers


def test_create_assessment_template(client, auth_headers):
    response = client.post('/assessment-templates', json={
        'name': 'Routine Health Assessment',
        'description': 'Standard intake assessment',
        'definition': {
            'fields': [
                {'name': 'blood_pressure', 'type': 'string', 'required': True},
                {'name': 'weight', 'type': 'number', 'required': False}
            ]
        }
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.get_json()['version']['version_number'] == 1


def test_record_service_delivery(client, doctor_headers):
    registered = client.post('/clients', json={'name': 'Service Delivery Client', 'age': 33}, headers=doctor_headers).get_json()
    response = client.post('/service-deliveries', json={
        'client_id': registered['id'],
        'service_type': 'health_screening',
        'outcome': 'completed',
        'notes': 'Routine screening completed',
        'answers': {'blood_pressure': '120/80', 'weight': 68}
    }, headers=doctor_headers)
    assert response.status_code == 201

    if response.status_code == 201:
        delivery_id = response.get_json()['id']
        correction = client.post(f'/service-deliveries/{delivery_id}/corrections', json={
            'reason': 'Corrected measurement entered by mistake',
            'outcome': 'completed',
            'notes': 'Routine screening completed; corrected weight',
            'answers': {'blood_pressure': '120/80', 'weight': 67}
        }, headers=doctor_headers)
        assert correction.status_code == 200


def test_service_delivery_is_tenant_scoped(client, doctor_headers):
    response = client.post('/service-deliveries', json={
        'client_id': 'nonexistent-client',
        'service_type': 'health_screening',
        'answers': {}
    }, headers=doctor_headers)
    assert response.status_code == 404

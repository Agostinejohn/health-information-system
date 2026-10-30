from tests import app, client, auth_headers, doctor_headers


def test_dashboard_returns_tenant_metrics(client, doctor_headers):
    response = client.get('/reports/dashboard', headers=doctor_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['active_clients'] >= 0
    assert data['active_enrollments'] >= 0
    assert data['service_deliveries'] >= 0


def test_program_summary(client, auth_headers):
    client.post('/programs', json={'name': 'Reporting Programme'}, headers=auth_headers)
    response = client.get('/reports/programs', headers=auth_headers)
    assert response.status_code == 200
    assert any(item['name'] == 'Reporting Programme' for item in response.get_json())


def test_create_clients_csv_export(client, auth_headers, doctor_headers):
    client.post('/clients', json={'name': 'Reported Client', 'age': 30}, headers=doctor_headers)
    response = client.post('/reports/exports', json={'report_type': 'clients'}, headers=auth_headers)
    assert response.status_code == 201
    data = response.get_json()
    assert data['report_type'] == 'clients'
    assert data['record_count'] >= 1
    assert 'name' in data['csv']


def test_download_cross_tenant_export_is_not_found(client, auth_headers):
    created = client.post('/reports/exports', json={'report_type': 'clients'}, headers=auth_headers).get_json()

    client.post('/auth/register', json={'email': 'report-other@example.com', 'password': 'password123', 'role': 'doctor'})
    login = client.post('/auth/login', json={'email': 'report-other@example.com', 'password': 'password123'}).get_json()
    other_org = client.post('/organizations', json={'name': 'Other Reporting Organisation'}, headers={'Authorization': f"Bearer {login['access_token']}"}).get_json()

    response = client.get(f"/reports/exports/{created['id']}/csv", headers={
        'Authorization': f"Bearer {login['access_token']}",
        'X-Organization-ID': other_org['id']
    })
    assert response.status_code == 404


def test_unsupported_report_type(client, auth_headers):
    response = client.post('/reports/exports', json={'report_type': 'unknown'}, headers=auth_headers)
    assert response.status_code == 400

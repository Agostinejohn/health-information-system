from tests import app, client


def test_health_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_liveness_endpoint(client):
    response = client.get('/health/live')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'alive'}


def test_readiness_endpoint(client):
    response = client.get('/health/ready')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ready'}

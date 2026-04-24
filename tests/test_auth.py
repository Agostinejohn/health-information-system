from tests import app, client

def test_register_success(client):
    res = client.post('/auth/register', json={
        'email': 'user@test.com',
        'password': 'password123',
        'role': 'doctor'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['email'] == 'user@test.com'
    assert data['role'] == 'doctor'
    assert 'password_hash' not in data

def test_register_duplicate_email(client):
    client.post('/auth/register', json={'email': 'dup@test.com', 'password': 'pass123', 'role': 'doctor'})
    res = client.post('/auth/register', json={'email': 'dup@test.com', 'password': 'pass123', 'role': 'doctor'})
    assert res.status_code == 409

def test_register_missing_fields(client):
    res = client.post('/auth/register', json={'email': 'bad@test.com'})
    assert res.status_code == 400
    assert 'errors' in res.get_json()

def test_register_invalid_email(client):
    res = client.post('/auth/register', json={'email': 'not-an-email', 'password': 'pass123'})
    assert res.status_code == 400

def test_register_short_password(client):
    res = client.post('/auth/register', json={'email': 'x@test.com', 'password': '123'})
    assert res.status_code == 400

def test_login_success(client):
    client.post('/auth/register', json={'email': 'login@test.com', 'password': 'pass123', 'role': 'doctor'})
    res = client.post('/auth/login', json={'email': 'login@test.com', 'password': 'pass123'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'access_token' in data
    assert data['user']['email'] == 'login@test.com'

def test_login_wrong_password(client):
    client.post('/auth/register', json={'email': 'wp@test.com', 'password': 'pass123', 'role': 'doctor'})
    res = client.post('/auth/login', json={'email': 'wp@test.com', 'password': 'wrongpass'})
    assert res.status_code == 401

def test_login_nonexistent_user(client):
    res = client.post('/auth/login', json={'email': 'ghost@test.com', 'password': 'pass123'})
    assert res.status_code == 401

def test_protected_route_without_token(client):
    res = client.get('/clients?name=John')
    assert res.status_code == 401

import pytest
from app import create_app
from app.db import db as _db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-jwt-secret'
    SECRET_KEY = 'test-secret'

@pytest.fixture(scope='function')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def auth_headers(client):
    """Register an admin and return JWT headers."""
    client.post('/auth/register', json={
        'email': 'admin@test.com',
        'password': 'password123',
        'role': 'admin'
    })
    res = client.post('/auth/login', json={
        'email': 'admin@test.com',
        'password': 'password123'
    })
    token = res.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture(scope='function')
def doctor_headers(client):
    """Register a doctor and return JWT headers."""
    client.post('/auth/register', json={
        'email': 'doctor@test.com',
        'password': 'password123',
        'role': 'doctor'
    })
    res = client.post('/auth/login', json={
        'email': 'doctor@test.com',
        'password': 'password123'
    })
    token = res.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

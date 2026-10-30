import pytest
from app import create_app
from app.db import db as _db
from app.models.organization import OrganizationMembership
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-jwt-secret-key-with-enough-length-123456'
    SECRET_KEY = 'test-secret-key-with-enough-length-123456789'

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
def auth_headers(client, app):
    """Register an admin, create an organization, and return tenant headers."""
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
    headers = {'Authorization': f'Bearer {token}'}
    org_res = client.post('/organizations', json={'name': 'Test Health Organization'}, headers=headers)
    organization_id = org_res.get_json()['id']
    return {**headers, 'X-Organization-ID': organization_id}

@pytest.fixture(scope='function')
def doctor_headers(client, app, auth_headers):
    """Register a doctor as a member of the shared test organization."""
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

    from app.models.user import User
    organization_id = auth_headers['X-Organization-ID']
    with app.app_context():
        doctor = User.query.filter_by(email='doctor@test.com').first()
        _db.session.add(OrganizationMembership(
            organization_id=organization_id,
            user_id=doctor.id,
            role='doctor',
            status='active'
        ))
        _db.session.commit()

    return {'Authorization': f'Bearer {token}', 'X-Organization-ID': organization_id}

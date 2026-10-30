from tests import app, client, auth_headers, doctor_headers
from app.models.user import User
from app.models.organization import OrganizationMembership
from app.db import db


def test_create_and_list_organization(client, auth_headers):
    response = client.post('/organizations', json={'name': 'Community Clinic'}, headers=auth_headers)
    assert response.status_code == 201
    organization = response.get_json()
    assert organization['name'] == 'Community Clinic'

    response = client.get('/organizations', headers=auth_headers)
    assert response.status_code == 200
    assert any(item['id'] == organization['id'] for item in response.get_json())


def test_organization_owner_has_access(client, auth_headers):
    organization_id = auth_headers['X-Organization-ID']
    response = client.get(
        f'/organizations/{organization_id}',
        headers=auth_headers
    )
    assert response.status_code == 200


def test_user_cannot_access_organization_without_membership(client, auth_headers):
    other = client.post('/auth/register', json={
        'email': 'other@test.com',
        'password': 'password123',
        'role': 'doctor'
    })
    assert other.status_code == 201

    login = client.post('/auth/login', json={
        'email': 'other@test.com',
        'password': 'password123'
    })
    headers = {
        'Authorization': 'Bearer ' + login.get_json()['access_token'],
        'X-Organization-ID': auth_headers['X-Organization-ID']
    }

    response = client.get(
        f"/organizations/{auth_headers['X-Organization-ID']}",
        headers=headers
    )
    assert response.status_code == 403


def test_admin_can_invite_member(client, auth_headers, app):
    organization_id = auth_headers['X-Organization-ID']
    response = client.post(
        f'/organizations/{organization_id}/invitations',
        json={'email': 'invited@test.com', 'role': 'doctor'},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.get_json()['email'] == 'invited@test.com'
    assert response.get_json()['role'] == 'doctor'
    assert response.get_json()['invite_token']


def test_invited_user_cannot_accept_before_registration(client, auth_headers):
    organization_id = auth_headers['X-Organization-ID']
    invitation = client.post(
        f'/organizations/{organization_id}/invitations',
        json={'email': 'future@test.com', 'role': 'staff'},
        headers=auth_headers
    ).get_json()

    response = client.post('/organizations/invitations/accept', json={
        'token': invitation['invite_token']
    }, headers=auth_headers)
    assert response.status_code == 400


def test_cross_tenant_client_is_not_visible(client, auth_headers, doctor_headers):
    created = client.post('/clients', json={'name': 'Tenant One Client', 'age': 30}, headers=doctor_headers)
    assert created.status_code == 201
    client_id = created.get_json()['id']

    client.post('/auth/register', json={
        'email': 'tenant2@test.com',
        'password': 'password123',
        'role': 'doctor'
    })
    login = client.post('/auth/login', json={
        'email': 'tenant2@test.com',
        'password': 'password123'
    })
    tenant2_token = login.get_json()['access_token']
    tenant2_org = client.post('/organizations', json={'name': 'Second Clinic'}, headers={
        'Authorization': f'Bearer {tenant2_token}'
    }).get_json()

    tenant2_headers = {
        'Authorization': f'Bearer {tenant2_token}',
        'X-Organization-ID': tenant2_org['id']
    }
    response = client.get(f'/clients/{client_id}', headers=tenant2_headers)
    assert response.status_code == 404

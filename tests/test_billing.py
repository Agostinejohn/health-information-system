from tests import app, client, auth_headers
from app.db import db
from app.models.billing import Invoice, OrganizationSubscription

def test_create_plan_and_change_subscription(client, auth_headers):
    plan = client.post('/billing/plans', json={
        'code': 'professional',
        'name': 'Professional',
        'monthly_price': '49.00',
        'currency': 'USD',
        'max_users': 25,
        'max_clients': 5000,
        'entitlements': {'reports': True, 'api_imports': True}
    }, headers=auth_headers)
    assert plan.status_code in (201, 409)

    changed = client.post('/billing/subscription/change-plan', json={
        'plan_code': 'professional'
    }, headers=auth_headers)
    assert changed.status_code == 200
    assert changed.get_json()['plan']['code'] == 'professional'

    entitlements = client.get('/billing/entitlements', headers=auth_headers)
    assert entitlements.status_code == 200
    assert entitlements.get_json()['reports'] is True


def test_subscription_lifecycle(client, auth_headers):
    client.post('/billing/plans', json={
        'code': 'starter',
        'name': 'Starter',
        'monthly_price': '19.00',
        'currency': 'USD',
        'entitlements': {'reports': True}
    }, headers=auth_headers)
    client.post('/billing/subscription/change-plan', json={'plan_code': 'starter'}, headers=auth_headers)

    suspended = client.post('/billing/subscription/lifecycle', json={
        'action': 'suspend', 'reason': 'Payment review'
    }, headers=auth_headers)
    assert suspended.status_code == 200
    assert suspended.get_json()['status'] == 'suspended'

    restricted = client.get('/billing/entitlements', headers=auth_headers)
    assert restricted.status_code == 402

    restored = client.post('/billing/subscription/lifecycle', json={
        'action': 'restore'
    }, headers=auth_headers)
    assert restored.status_code == 200
    assert restored.get_json()['status'] == 'active'

    cancelled = client.post('/billing/subscription/lifecycle', json={
        'action': 'cancel', 'reason': 'Customer request'
    }, headers=auth_headers)
    assert cancelled.status_code == 200
    assert cancelled.get_json()['status'] == 'cancelled'


def test_invoice_lifecycle(client, auth_headers):
    client.post('/billing/plans', json={
        'code': 'invoice-test',
        'name': 'Invoice Test',
        'monthly_price': '10.00',
        'currency': 'USD',
        'entitlements': {}
    }, headers=auth_headers)
    subscription = client.post('/billing/subscription/change-plan', json={'plan_code': 'invoice-test'}, headers=auth_headers)
    assert subscription.status_code == 200

    organization_id = auth_headers['X-Organization-ID']
    subscription = OrganizationSubscription.query.filter_by(organization_id=organization_id).first()
    invoice = Invoice(organization_id=organization_id, subscription_id=subscription.id,
                      provider_invoice_id='manual-provider-invoice-1', status='open', amount=10, currency='USD')
    db.session.add(invoice)
    db.session.commit()

    updated = client.post(f'/billing/invoices/{invoice.id}/status', json={
        'status': 'paid',
        'provider_invoice_id': 'manual-provider-invoice-1'
    }, headers=auth_headers)
    assert updated.status_code == 200
    assert updated.get_json()['status'] == 'paid'

    listed = client.get('/billing/invoices', headers=auth_headers)
    assert listed.status_code == 200
    assert any(item['id'] == invoice.id for item in listed.get_json())

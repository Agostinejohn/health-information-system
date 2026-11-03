from datetime import datetime
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.authorization import organization_member_required
from app.models.billing import SubscriptionPlan, OrganizationSubscription, Invoice, UsageRecord
from app.schemas.billing import SubscriptionPlanSchema, SubscriptionChangeSchema, InvoiceStatusSchema, SubscriptionLifecycleSchema
from app.services.billing_service import (
    create_plan, ensure_subscription, change_plan, change_subscription_lifecycle,
    subscription_entitlements, record_invoice, update_invoice_status, record_usage
)

billing_bp = Blueprint('billing', __name__)
plan_schema = SubscriptionPlanSchema()
change_schema = SubscriptionChangeSchema()
invoice_schema = InvoiceStatusSchema()
lifecycle_schema = SubscriptionLifecycleSchema()


def _subscription_json(subscription):
    return {'id': subscription.id, 'organization_id': subscription.organization_id,
            'status': subscription.status, 'plan': {'code': subscription.plan.code, 'name': subscription.plan.name},
            'trial_end': subscription.trial_end.isoformat() if subscription.trial_end else None,
            'cancelled_at': subscription.cancelled_at.isoformat() if subscription.cancelled_at else None,
            'suspended_at': subscription.suspended_at.isoformat() if subscription.suspended_at else None}


@billing_bp.get('/billing/plans')
@organization_member_required()
def list_plans(user, membership):
    plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.monthly_price).all()
    return jsonify([{'id': item.id, 'code': item.code, 'name': item.name, 'monthly_price': str(item.monthly_price),
                     'currency': item.currency, 'max_users': item.max_users, 'max_clients': item.max_clients,
                     'entitlements': item.entitlements} for item in plans]), 200


@billing_bp.post('/billing/plans')
@organization_member_required({'owner', 'admin'})
def create_plan_route(user, membership):
    try:
        data = plan_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    data['monthly_price'] = str(data['monthly_price'])
    plan, error = create_plan(data)
    if error:
        return jsonify({'error': error}), 409
    return jsonify({'id': plan.id, 'code': plan.code, 'name': plan.name}), 201


@billing_bp.get('/billing/subscription')
@organization_member_required()
def get_subscription(user, membership):
    subscription = OrganizationSubscription.query.filter_by(organization_id=request.organization_id).first()
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    return jsonify(_subscription_json(subscription)), 200


@billing_bp.post('/billing/subscription/change-plan')
@organization_member_required({'owner', 'admin'})
def change_subscription_plan(user, membership):
    try:
        data = change_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    subscription, error = change_plan(request.organization_id, data['plan_code'], user.id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(_subscription_json(subscription)), 200


@billing_bp.post('/billing/subscription/lifecycle')
@organization_member_required({'owner', 'admin'})
def subscription_lifecycle(user, membership):
    try:
        data = lifecycle_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    subscription, error = change_subscription_lifecycle(request.organization_id, data['action'], data.get('reason'), user.id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(_subscription_json(subscription)), 200


@billing_bp.get('/billing/entitlements')
@organization_member_required()
def entitlements(user, membership):
    entitlements, error = subscription_entitlements(request.organization_id)
    if error:
        return jsonify({'error': error}), 402
    return jsonify(entitlements), 200


@billing_bp.get('/billing/invoices')
@organization_member_required({'owner', 'admin'})
def list_invoices(user, membership):
    invoices = Invoice.query.filter_by(organization_id=request.organization_id).order_by(Invoice.issued_at.desc()).all()
    return jsonify([{'id': item.id, 'status': item.status, 'amount': str(item.amount), 'currency': item.currency,
                     'provider_invoice_id': item.provider_invoice_id, 'issued_at': item.issued_at.isoformat()} for item in invoices]), 200


@billing_bp.post('/billing/invoices/<invoice_id>/status')
@organization_member_required({'owner', 'admin'})
def update_invoice(user, membership, invoice_id):
    invoice = Invoice.query.filter_by(id=invoice_id, organization_id=request.organization_id).first()
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404
    try:
        data = invoice_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    update_invoice_status(invoice, data['status'], data.get('provider_invoice_id'))
    return jsonify({'id': invoice.id, 'status': invoice.status, 'provider_invoice_id': invoice.provider_invoice_id}), 200


@billing_bp.get('/billing/usage')
@organization_member_required({'owner', 'admin', 'manager'})
def usage(user, membership):
    records = UsageRecord.query.filter_by(organization_id=request.organization_id).order_by(UsageRecord.recorded_at.desc()).all()
    return jsonify([{'id': item.id, 'metric': item.metric, 'quantity': item.quantity,
                     'period_start': item.period_start.isoformat(), 'period_end': item.period_end.isoformat()} for item in records]), 200

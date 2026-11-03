from datetime import datetime, timezone
from app.db import db
from app.models.billing import SubscriptionPlan, OrganizationSubscription, Invoice, UsageRecord, BillingEvent
from app.models.organization import Organization


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_plan(data):
    if SubscriptionPlan.query.filter_by(code=data['code']).first():
        return None, 'Plan code already exists'
    plan = SubscriptionPlan(**data)
    db.session.add(plan)
    db.session.commit()
    return plan, None


def ensure_subscription(organization_id, plan_code='starter'):
    subscription = OrganizationSubscription.query.filter_by(organization_id=organization_id).first()
    if subscription:
        return subscription
    plan = SubscriptionPlan.query.filter_by(code=plan_code, is_active=True).first()
    if not plan:
        return None
    subscription = OrganizationSubscription(organization_id=organization_id, plan_id=plan.id, status='trialing', trial_end=None)
    db.session.add(subscription)
    db.session.commit()
    return subscription


def change_plan(organization_id, plan_code, actor_id=None):
    plan = SubscriptionPlan.query.filter_by(code=plan_code, is_active=True).first()
    if not plan:
        return None, 'Plan not found'
    subscription = OrganizationSubscription.query.filter_by(organization_id=organization_id).first()
    if not subscription:
        subscription = OrganizationSubscription(organization_id=organization_id, plan_id=plan.id, status='trialing')
        db.session.add(subscription)
        db.session.flush()
    else:
        subscription.plan_id = plan.id
        if subscription.status == 'cancelled':
            subscription.status = 'active'
            subscription.cancelled_at = None
    db.session.add(BillingEvent(organization_id=organization_id, subscription_id=subscription.id,
                                event_type='subscription.plan_changed',
                                details={'plan_code': plan.code}, actor_id=actor_id))
    db.session.commit()
    return subscription, None


def change_subscription_lifecycle(organization_id, action, reason=None, actor_id=None):
    subscription = OrganizationSubscription.query.filter_by(organization_id=organization_id).first()
    if not subscription:
        return None, 'Subscription not found'
    now = utc_now()
    if action == 'cancel':
        subscription.status = 'cancelled'
        subscription.cancelled_at = now
    elif action == 'restore':
        subscription.status = 'active'
        subscription.cancelled_at = None
        subscription.suspended_at = None
    elif action == 'suspend':
        subscription.status = 'suspended'
        subscription.suspended_at = now
    db.session.add(BillingEvent(organization_id=organization_id, subscription_id=subscription.id,
                                event_type=f'subscription.{action}', details={'reason': reason}, actor_id=actor_id))
    db.session.commit()
    return subscription, None


def subscription_entitlements(organization_id):
    subscription = OrganizationSubscription.query.filter_by(organization_id=organization_id).first()
    if not subscription or subscription.status in {'cancelled', 'suspended'}:
        return None, 'Subscription is not active'
    return subscription.plan.entitlements or {}, None


def record_invoice(organization_id, subscription, amount, currency='USD', provider_invoice_id=None):
    invoice = Invoice(organization_id=organization_id, subscription_id=subscription.id, amount=amount,
                      currency=currency, provider_invoice_id=provider_invoice_id, status='open')
    db.session.add(invoice)
    db.session.commit()
    return invoice


def update_invoice_status(invoice, status, provider_invoice_id=None):
    invoice.status = status
    if provider_invoice_id:
        invoice.provider_invoice_id = provider_invoice_id
    if status == 'paid':
        invoice.paid_at = utc_now()
    db.session.commit()
    return invoice


def record_usage(organization_id, metric, quantity, period_start, period_end):
    usage = UsageRecord(organization_id=organization_id, metric=metric, quantity=quantity,
                        period_start=period_start, period_end=period_end)
    db.session.add(usage)
    db.session.commit()
    return usage

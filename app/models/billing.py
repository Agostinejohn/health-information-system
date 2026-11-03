import uuid
from app.db import db


class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(50), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    monthly_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    max_users = db.Column(db.Integer, nullable=True)
    max_clients = db.Column(db.Integer, nullable=True)
    entitlements = db.Column(db.JSON, nullable=False, default=dict)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class OrganizationSubscription(db.Model):
    __tablename__ = 'organization_subscriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    plan_id = db.Column(db.String(36), db.ForeignKey('subscription_plans.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='trialing')
    billing_provider = db.Column(db.String(50), nullable=True)
    provider_customer_id = db.Column(db.String(255), nullable=True)
    provider_subscription_id = db.Column(db.String(255), nullable=True)
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    trial_end = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    suspended_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    plan = db.relationship('SubscriptionPlan')


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    subscription_id = db.Column(db.String(36), db.ForeignKey('organization_subscriptions.id', ondelete='CASCADE'), nullable=False, index=True)
    provider_invoice_id = db.Column(db.String(255), nullable=True, unique=True)
    status = db.Column(db.String(20), nullable=False, default='draft')
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    issued_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    due_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)


class UsageRecord(db.Model):
    __tablename__ = 'usage_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    metric = db.Column(db.String(50), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    period_start = db.Column(db.DateTime, nullable=False)
    period_end = db.Column(db.DateTime, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class BillingEvent(db.Model):
    __tablename__ = 'billing_events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    subscription_id = db.Column(db.String(36), db.ForeignKey('organization_subscriptions.id', ondelete='CASCADE'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    details = db.Column(db.JSON, nullable=False, default=dict)
    actor_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

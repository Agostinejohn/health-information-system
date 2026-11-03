import uuid
from app.db import db


class IntegrationCredential(db.Model):
    __tablename__ = 'integration_credentials'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    credential_type = db.Column(db.String(50), nullable=False, default='api')
    key_prefix = db.Column(db.String(20), nullable=False)
    key_hash = db.Column(db.String(64), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    revoked_at = db.Column(db.DateTime, nullable=True)


class IdempotencyRecord(db.Model):
    __tablename__ = 'idempotency_records'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    idempotency_key = db.Column(db.String(255), nullable=False)
    request_path = db.Column(db.String(255), nullable=False)
    request_hash = db.Column(db.String(64), nullable=False)
    response_status = db.Column(db.Integer, nullable=False)
    response_body = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint('organization_id', 'idempotency_key', 'request_path', name='uq_idempotency_request'),)


class WebhookEndpoint(db.Model):
    __tablename__ = 'webhook_endpoints'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(2048), nullable=False)
    secret_hash = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class WebhookDelivery(db.Model):
    __tablename__ = 'webhook_deliveries'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = db.Column(db.String(36), db.ForeignKey('webhook_endpoints.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    attempt_count = db.Column(db.Integer, nullable=False, default=0)
    response_status = db.Column(db.Integer, nullable=True)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    delivered_at = db.Column(db.DateTime, nullable=True)

import uuid
from app.db import db


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    timezone = db.Column(db.String(50), nullable=False, default='UTC')
    reason = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='scheduled', index=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)


class FollowUp(db.Model):
    __tablename__ = 'follow_ups'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    assigned_to = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    due_at = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='normal', index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending', index=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)


class Referral(db.Model):
    __tablename__ = 'referrals'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    destination = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='normal')
    status = db.Column(db.String(20), nullable=False, default='referred', index=True)
    referred_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    referred_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    outcome = db.Column(db.Text, nullable=True)
    outcome_at = db.Column(db.DateTime, nullable=True)

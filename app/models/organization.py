import uuid
from app.db import db


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), nullable=False, unique=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'slug': self.slug, 'is_active': self.is_active}


class OrganizationMembership(db.Model):
    __tablename__ = 'organization_memberships'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    organization = db.relationship('Organization', backref='memberships')
    user = db.relationship('User', backref='organization_memberships')

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'user_id', name='uq_membership_organization_user'),
    )


class OrganizationInvitation(db.Model):
    __tablename__ = 'organization_invitations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)
    token_hash = db.Column(db.String(64), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    invited_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    organization = db.relationship('Organization', backref='invitations')
    inviter = db.relationship('User', foreign_keys=[invited_by])

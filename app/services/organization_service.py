import re
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from app.db import db
from app.models.organization import Organization, OrganizationMembership, OrganizationInvitation
from app.models.user import User

VALID_MEMBERSHIP_ROLES = {'owner', 'admin', 'manager', 'doctor', 'staff'}


def _slugify(value):
    value = value.strip().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value)
    return value.strip('-')[:120]


def create_organization(name, owner):
    base_slug = _slugify(name)
    if not base_slug:
        return None, 'A valid organization name is required'

    slug = base_slug
    suffix = 2
    while Organization.query.filter_by(slug=slug).first():
        slug = f'{base_slug}-{suffix}'
        suffix += 1

    organization = Organization(name=name.strip(), slug=slug)
    db.session.add(organization)
    db.session.flush()

    membership = OrganizationMembership(
        organization_id=organization.id,
        user_id=owner.id,
        role='owner',
        status='active'
    )
    db.session.add(membership)
    db.session.commit()
    return organization, None


def get_active_membership(user_id, organization_id):
    return OrganizationMembership.query.filter_by(
        user_id=user_id,
        organization_id=organization_id,
        status='active'
    ).first()


def list_user_organizations(user_id):
    memberships = OrganizationMembership.query.filter_by(user_id=user_id, status='active').all()
    organization_ids = [membership.organization_id for membership in memberships]
    if not organization_ids:
        return []
    organizations = Organization.query.filter(Organization.id.in_(organization_ids)).all()
    return organizations


def invite_member(organization_id, inviter, email, role):
    if role not in VALID_MEMBERSHIP_ROLES or role == 'owner':
        return None, 'Invalid member role'

    normalized_email = email.strip().lower()
    if OrganizationInvitation.query.filter_by(
        organization_id=organization_id,
        email=normalized_email,
        status='pending'
    ).first():
        return None, 'A pending invitation already exists'

    existing_user = User.query.filter_by(email=normalized_email).first()
    if existing_user:
        existing_membership = get_active_membership(existing_user.id, organization_id)
        if existing_membership:
            return None, 'User is already a member'

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
    invitation = OrganizationInvitation(
        organization_id=organization_id,
        email=normalized_email,
        role=role,
        token_hash=token_hash,
        invited_by=inviter.id,
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7)
    )
    db.session.add(invitation)
    db.session.commit()
    return {'invitation': invitation, 'token': raw_token}, None


def accept_invitation(token, user):
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    invitation = OrganizationInvitation.query.filter_by(token_hash=token_hash).first()
    if not invitation:
        return None, 'Invitation not found'
    if invitation.status != 'pending':
        return None, 'Invitation is no longer valid'
    if invitation.expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        invitation.status = 'expired'
        db.session.commit()
        return None, 'Invitation has expired'
    if user.email.lower() != invitation.email.lower():
        return None, 'Invitation belongs to a different user'

    membership = get_active_membership(user.id, invitation.organization_id)
    if membership:
        invitation.status = 'accepted'
        db.session.commit()
        return membership, None

    membership = OrganizationMembership(
        organization_id=invitation.organization_id,
        user_id=user.id,
        role=invitation.role,
        status='active'
    )
    invitation.status = 'accepted'
    db.session.add(membership)
    db.session.commit()
    return membership, None

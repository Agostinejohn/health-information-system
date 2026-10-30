from datetime import datetime, timezone
from app.db import db
from app.models.care_work import Appointment, FollowUp, Referral
from app.models.client import Client
from app.models.program import Program
from app.models.user import User
from app.models.organization import OrganizationMembership


def _tenant_client(client_id, organization_id):
    return Client.query.filter_by(id=client_id, organization_id=organization_id, status='active').first()


def _tenant_program(program_id, organization_id):
    if not program_id:
        return None
    return Program.query.filter_by(id=program_id, organization_id=organization_id).first()


def _tenant_user(user_id, organization_id):
    if not user_id:
        return None
    return User.query.join(OrganizationMembership).filter(
        User.id == user_id,
        OrganizationMembership.organization_id == organization_id,
        OrganizationMembership.status == 'active'
    ).first()


def _utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_appointment(organization_id, actor_id, data):
    if not _tenant_client(data['client_id'], organization_id):
        return None, 'Client not found'
    if data.get('program_id') and not _tenant_program(data['program_id'], organization_id):
        return None, 'Program not found'
    if data.get('assigned_to') and not _tenant_user(data['assigned_to'], organization_id):
        return None, 'Assigned user is not an organization member'
    appointment = Appointment(organization_id=organization_id, created_by=actor_id, **data)
    db.session.add(appointment)
    db.session.commit()
    return appointment, None


def update_appointment_status(appointment, status, notes=None):
    appointment.status = status
    if notes is not None:
        appointment.notes = notes
    if status in {'completed', 'cancelled', 'no_show'}:
        appointment.completed_at = _utc_now()
    db.session.commit()
    return appointment


def list_appointments(organization_id, client_id=None):
    query = Appointment.query.filter_by(organization_id=organization_id)
    if client_id:
        query = query.filter_by(client_id=client_id)
    return query.order_by(Appointment.scheduled_at.asc()).all()


def create_follow_up(organization_id, actor_id, data):
    if not _tenant_client(data['client_id'], organization_id):
        return None, 'Client not found'
    if data.get('program_id') and not _tenant_program(data['program_id'], organization_id):
        return None, 'Program not found'
    if data.get('assigned_to') and not _tenant_user(data['assigned_to'], organization_id):
        return None, 'Assigned user is not an organization member'
    follow_up = FollowUp(organization_id=organization_id, created_by=actor_id, **data)
    db.session.add(follow_up)
    db.session.commit()
    return follow_up, None


def update_follow_up_status(follow_up, status):
    follow_up.status = status
    if status == 'completed':
        follow_up.completed_at = _utc_now()
    db.session.commit()
    return follow_up


def list_follow_ups(organization_id, assigned_to=None, status=None):
    query = FollowUp.query.filter_by(organization_id=organization_id)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(FollowUp.due_at.asc()).all()


def create_referral(organization_id, actor_id, data):
    if not _tenant_client(data['client_id'], organization_id):
        return None, 'Client not found'
    if data.get('program_id') and not _tenant_program(data['program_id'], organization_id):
        return None, 'Program not found'
    referral = Referral(organization_id=organization_id, referred_by=actor_id, **data)
    db.session.add(referral)
    db.session.commit()
    return referral, None


def update_referral_status(referral, status, outcome=None):
    referral.status = status
    if outcome is not None:
        referral.outcome = outcome
    if status in {'completed', 'declined', 'cancelled'}:
        referral.outcome_at = _utc_now()
    db.session.commit()
    return referral


def list_referrals(organization_id, client_id=None, status=None):
    query = Referral.query.filter_by(organization_id=organization_id)
    if client_id:
        query = query.filter_by(client_id=client_id)
    if status:
        query = query.filter_by(status=status)
    return query.order_by(Referral.referred_at.desc()).all()

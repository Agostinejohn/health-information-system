from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.authorization import organization_member_required
from app.models.care_work import Appointment, FollowUp, Referral
from app.schemas.care_work import (
    AppointmentSchema, AppointmentStatusSchema, FollowUpSchema,
    FollowUpStatusSchema, ReferralSchema, ReferralStatusSchema
)
from app.services.care_work_service import (
    create_appointment, update_appointment_status, list_appointments,
    create_follow_up, update_follow_up_status, list_follow_ups,
    create_referral, update_referral_status, list_referrals
)

care_work_bp = Blueprint('care_work', __name__)
appointment_schema = AppointmentSchema()
appointment_status_schema = AppointmentStatusSchema()
follow_up_schema = FollowUpSchema()
follow_up_status_schema = FollowUpStatusSchema()
referral_schema = ReferralSchema()
referral_status_schema = ReferralStatusSchema()


def _serialize_appointment(item):
    return {'id': item.id, 'client_id': item.client_id, 'program_id': item.program_id,
            'assigned_to': item.assigned_to, 'scheduled_at': item.scheduled_at.isoformat(),
            'timezone': item.timezone, 'reason': item.reason, 'notes': item.notes,
            'status': item.status, 'completed_at': item.completed_at.isoformat() if item.completed_at else None}


def _serialize_follow_up(item):
    return {'id': item.id, 'client_id': item.client_id, 'program_id': item.program_id,
            'assigned_to': item.assigned_to, 'due_at': item.due_at.isoformat(),
            'priority': item.priority, 'title': item.title, 'description': item.description,
            'status': item.status, 'completed_at': item.completed_at.isoformat() if item.completed_at else None}


def _serialize_referral(item):
    return {'id': item.id, 'client_id': item.client_id, 'program_id': item.program_id,
            'destination': item.destination, 'reason': item.reason, 'priority': item.priority,
            'status': item.status, 'outcome': item.outcome,
            'outcome_at': item.outcome_at.isoformat() if item.outcome_at else None}


@care_work_bp.get('/appointments')
@organization_member_required()
def appointments(user, membership):
    return jsonify([_serialize_appointment(item) for item in list_appointments(
        request.organization_id, request.args.get('client_id'))]), 200


@care_work_bp.post('/appointments')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def create_appointment_route(user, membership):
    try:
        data = appointment_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    appointment, error = create_appointment(request.organization_id, user.id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(_serialize_appointment(appointment)), 201


@care_work_bp.patch('/appointments/<appointment_id>')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def appointment_status(user, membership, appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id, organization_id=request.organization_id).first()
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    try:
        data = appointment_status_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    return jsonify(_serialize_appointment(update_appointment_status(appointment, data['status'], data.get('notes')))), 200


@care_work_bp.get('/follow-ups')
@organization_member_required()
def follow_ups(user, membership):
    items = list_follow_ups(request.organization_id, request.args.get('assigned_to'), request.args.get('status'))
    return jsonify([_serialize_follow_up(item) for item in items]), 200


@care_work_bp.post('/follow-ups')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def create_follow_up_route(user, membership):
    try:
        data = follow_up_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    item, error = create_follow_up(request.organization_id, user.id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(_serialize_follow_up(item)), 201


@care_work_bp.patch('/follow-ups/<follow_up_id>')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def follow_up_status(user, membership, follow_up_id):
    item = FollowUp.query.filter_by(id=follow_up_id, organization_id=request.organization_id).first()
    if not item:
        return jsonify({'error': 'Follow-up not found'}), 404
    try:
        data = follow_up_status_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    return jsonify(_serialize_follow_up(update_follow_up_status(item, data['status']))), 200


@care_work_bp.get('/referrals')
@organization_member_required()
def referrals(user, membership):
    items = list_referrals(request.organization_id, request.args.get('client_id'), request.args.get('status'))
    return jsonify([_serialize_referral(item) for item in items]), 200


@care_work_bp.post('/referrals')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def create_referral_route(user, membership):
    try:
        data = referral_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    item, error = create_referral(request.organization_id, user.id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(_serialize_referral(item)), 201


@care_work_bp.patch('/referrals/<referral_id>')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def referral_status(user, membership, referral_id):
    item = Referral.query.filter_by(id=referral_id, organization_id=request.organization_id).first()
    if not item:
        return jsonify({'error': 'Referral not found'}), 404
    try:
        data = referral_status_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    return jsonify(_serialize_referral(update_referral_status(item, data['status'], data.get('outcome')))), 200

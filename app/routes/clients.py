from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.authorization import organization_member_required
from app.schemas.client import ClientSchema, ConsentSchema, ClientDocumentSchema, EnrollSchema
from app.schemas.program import EnrollmentStatusSchema
from app.services.client_service import (
    register_client, search_clients, get_client, enroll_client,
    find_duplicate_candidates, record_consent, record_document, get_client_timeline,
    update_enrollment_status
)

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')
client_schema = ClientSchema()
consent_schema = ConsentSchema()
document_schema = ClientDocumentSchema()
enroll_schema = EnrollSchema()
enrollment_status_schema = EnrollmentStatusSchema()

@clients_bp.route('', methods=['POST'])
@organization_member_required()
def create(user, membership):
    try:
        data = client_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    duplicates = find_duplicate_candidates(
        data['name'], request.organization_id,
        email=data.get('email'), phone=data.get('phone'),
        external_reference=data.get('external_reference')
    )
    if duplicates:
        return jsonify({
            'error': 'Possible duplicate client found',
            'duplicates': [client.to_dict() for client in duplicates]
        }), 409

    client = register_client(
        data['name'], data['age'], request.organization_id,
        external_reference=data.get('external_reference'),
        email=data.get('email'), phone=data.get('phone'),
        address=data.get('address')
    )
    return jsonify(client.to_dict()), 201

@clients_bp.route('', methods=['GET'])
@organization_member_required()
def search(user, membership):
    name_query = request.args.get('name', '').strip()
    if not name_query:
        return jsonify({'error': 'name query param is required'}), 400

    clients = search_clients(name_query, request.organization_id)
    return jsonify([c.to_dict() for c in clients]), 200

@clients_bp.route('/<client_id>', methods=['GET'])
@organization_member_required()
def get_profile(user, membership, client_id):
    client = get_client(client_id, request.organization_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    return jsonify(client.to_dict(include_programs=True)), 200

@clients_bp.route('/<client_id>/consents', methods=['POST'])
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def add_consent(user, membership, client_id):
    try:
        data = consent_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    consent = record_consent(client_id, request.organization_id, user.id, **data)
    if not consent:
        return jsonify({'error': 'Client not found'}), 404
    return jsonify({'id': consent.id, 'consent_type': consent.consent_type, 'granted': consent.granted}), 201

@clients_bp.route('/<client_id>/documents', methods=['POST'])
@organization_member_required()
def add_document(user, membership, client_id):
    try:
        data = document_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    document = record_document(client_id, request.organization_id, user.id, **data)
    if not document:
        return jsonify({'error': 'Client not found'}), 404
    return jsonify({'id': document.id, 'title': document.title, 'storage_key': document.storage_key}), 201

@clients_bp.route('/<client_id>/timeline', methods=['GET'])
@organization_member_required()
def timeline(user, membership, client_id):
    events = get_client_timeline(client_id, request.organization_id)
    if events is None:
        return jsonify({'error': 'Client not found'}), 404
    return jsonify([{
        'id': event.id,
        'event_type': event.event_type,
        'title': event.title,
        'description': event.description,
        'created_at': event.created_at.isoformat()
    } for event in events]), 200

@clients_bp.route('/<client_id>/enroll', methods=['POST'])
@organization_member_required()
def enroll(user, membership, client_id):
    try:
        data = enroll_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    client, result = enroll_client(client_id, data['program_ids'], request.organization_id, user.id)
    if not client:
        return jsonify({'error': result}), 404

    return jsonify({
        'client': client.to_dict(include_programs=True),
        'enrollment_result': result
    }), 200

@clients_bp.route('/<client_id>/enrollments/<program_id>', methods=['PATCH'])
@organization_member_required({'owner', 'admin', 'manager'})
def update_enrollment_status_route(user, membership, client_id, program_id):
    try:
        data = enrollment_status_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    enrollment = update_enrollment_status(
        client_id, program_id, request.organization_id, **data
    )
    if not enrollment:
        return jsonify({'error': 'Enrollment not found'}), 404

    return jsonify({
        'id': enrollment.id,
        'status': enrollment.status,
        'reason': enrollment.reason,
        'ended_at': enrollment.ended_at.isoformat() if enrollment.ended_at else None
    }), 200

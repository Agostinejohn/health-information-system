from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.authorization import organization_member_required
from app.models.service_delivery import AssessmentTemplate, AssessmentTemplateVersion, ServiceDelivery
from app.schemas.service_delivery import AssessmentTemplateSchema, ServiceDeliverySchema, ServiceDeliveryCorrectionSchema
from app.services.service_delivery_service import create_template, create_service_delivery, correct_service_delivery

service_delivery_bp = Blueprint('service_delivery', __name__)
template_schema = AssessmentTemplateSchema()
delivery_schema = ServiceDeliverySchema()
correction_schema = ServiceDeliveryCorrectionSchema()


def _delivery_json(item):
    return {
        'id': item.id,
        'client_id': item.client_id,
        'program_id': item.program_id,
        'appointment_id': item.appointment_id,
        'template_version_id': item.template_version_id,
        'service_type': item.service_type,
        'outcome': item.outcome,
        'notes': item.notes,
        'answers': item.answers,
        'status': item.status,
        'provided_by': item.provided_by,
        'recorded_at': item.recorded_at.isoformat(),
        'corrected_at': item.corrected_at.isoformat() if item.corrected_at else None
    }


@service_delivery_bp.post('/assessment-templates')
@organization_member_required({'owner', 'admin', 'manager'})
def create_template_route(user, membership):
    try:
        data = template_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    template, version, error = create_template(request.organization_id, user.id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'id': template.id, 'name': template.name, 'version': {
        'id': version.id, 'version_number': version.version_number, 'definition': version.definition
    }}), 201


@service_delivery_bp.get('/assessment-templates')
@organization_member_required()
def list_templates(user, membership):
    templates = AssessmentTemplate.query.filter_by(organization_id=request.organization_id).order_by(AssessmentTemplate.created_at.desc()).all()
    result = []
    for template in templates:
        versions = AssessmentTemplateVersion.query.filter_by(template_id=template.id).order_by(AssessmentTemplateVersion.version_number.desc()).all()
        result.append({'id': template.id, 'name': template.name, 'description': template.description,
                       'versions': [{'id': item.id, 'version_number': item.version_number} for item in versions]})
    return jsonify(result), 200


@service_delivery_bp.post('/service-deliveries')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def create_delivery_route(user, membership):
    try:
        data = delivery_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    delivery, error = create_service_delivery(request.organization_id, user.id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(_delivery_json(delivery)), 201


@service_delivery_bp.get('/service-deliveries')
@organization_member_required()
def list_deliveries(user, membership):
    query = ServiceDelivery.query.filter_by(organization_id=request.organization_id)
    if request.args.get('client_id'):
        query = query.filter_by(client_id=request.args.get('client_id'))
    deliveries = query.order_by(ServiceDelivery.recorded_at.desc()).all()
    return jsonify([_delivery_json(item) for item in deliveries]), 200


@service_delivery_bp.post('/service-deliveries/<delivery_id>/corrections')
@organization_member_required({'owner', 'admin', 'manager', 'doctor'})
def correct_delivery_route(user, membership, delivery_id):
    delivery = ServiceDelivery.query.filter_by(id=delivery_id, organization_id=request.organization_id).first()
    if not delivery:
        return jsonify({'error': 'Service delivery not found'}), 404
    try:
        data = correction_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    delivery, correction = correct_service_delivery(delivery, request.organization_id, user.id, data)
    return jsonify({'service_delivery': _delivery_json(delivery), 'correction_id': correction.id}), 200

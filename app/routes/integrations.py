from flask import Blueprint, request, jsonify
import hashlib
import json
from marshmallow import ValidationError
from app.authorization import organization_member_required
from app.models.integration import IntegrationCredential, WebhookEndpoint, WebhookDelivery
from app.schemas.integration import ImportClientsSchema, CreateWebhookSchema, IntegrationCredentialSchema
from app.services.integration_service import (
    preview_client_import, commit_client_import, create_api_credential,
    revoke_api_credential, create_webhook, enqueue_webhook,
    get_idempotent_response, save_idempotent_response
)

integrations_bp = Blueprint('integrations', __name__)
import_schema = ImportClientsSchema()
webhook_schema = CreateWebhookSchema()
credential_schema = IntegrationCredentialSchema()


@integrations_bp.post('/integrations/imports/clients/preview')
@organization_member_required({'owner', 'admin', 'manager'})
def preview_client_import_route(user, membership):
    try:
        data = import_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    return jsonify(preview_client_import(request.organization_id, data['rows'])), 200


@integrations_bp.post('/integrations/imports/clients/commit')
@organization_member_required({'owner', 'admin', 'manager'})
def commit_client_import_route(user, membership):
    try:
        data = import_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400

    idempotency_key = request.headers.get('Idempotency-Key', '').strip()
    if not idempotency_key or len(idempotency_key) > 255:
        return jsonify({'error': 'Idempotency-Key header is required and must be 1-255 characters'}), 400

    request_hash = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    try:
        cached = get_idempotent_response(request.organization_id, idempotency_key, request.path, request_hash)
    except ValueError as error:
        return jsonify({'error': str(error)}), 409
    if cached:
        return jsonify(cached.response_body), cached.response_status

    result, error = commit_client_import(request.organization_id, data['rows'])
    if error:
        response = {'error': error}
        status = 409
    else:
        response = result
        status = 201
    save_idempotent_response(request.organization_id, idempotency_key, request.path, request_hash, status, response)
    return jsonify(response), status


@integrations_bp.post('/integrations/credentials')
@organization_member_required({'owner', 'admin'})
def create_credential(user, membership):
    try:
        data = credential_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    credential, raw_key = create_api_credential(request.organization_id, user.id, data['name'])
    return jsonify({'id': credential.id, 'name': credential.name, 'key_prefix': credential.key_prefix, 'api_key': raw_key}), 201


@integrations_bp.get('/integrations/credentials')
@organization_member_required({'owner', 'admin'})
def list_credentials(user, membership):
    credentials = IntegrationCredential.query.filter_by(organization_id=request.organization_id).order_by(IntegrationCredential.created_at.desc()).all()
    return jsonify([{'id': item.id, 'name': item.name, 'key_prefix': item.key_prefix, 'status': item.status} for item in credentials]), 200


@integrations_bp.post('/integrations/credentials/<credential_id>/revoke')
@organization_member_required({'owner', 'admin'})
def revoke_credential(user, membership, credential_id):
    credential = IntegrationCredential.query.filter_by(id=credential_id, organization_id=request.organization_id).first()
    if not credential:
        return jsonify({'error': 'Credential not found'}), 404
    revoke_api_credential(credential)
    return jsonify({'id': credential.id, 'status': credential.status}), 200


@integrations_bp.post('/integrations/webhooks')
@organization_member_required({'owner', 'admin'})
def create_webhook_route(user, membership):
    try:
        data = webhook_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400
    webhook, secret = create_webhook(request.organization_id, data['name'], data['url'])
    return jsonify({'id': webhook.id, 'name': webhook.name, 'url': webhook.url, 'signing_secret': secret}), 201


@integrations_bp.get('/integrations/webhooks')
@organization_member_required({'owner', 'admin'})
def list_webhooks(user, membership):
    endpoints = WebhookEndpoint.query.filter_by(organization_id=request.organization_id).order_by(WebhookEndpoint.created_at.desc()).all()
    return jsonify([{'id': item.id, 'name': item.name, 'url': item.url, 'status': item.status} for item in endpoints]), 200


@integrations_bp.post('/integrations/webhooks/<endpoint_id>/deliveries')
@organization_member_required({'owner', 'admin'})
def enqueue_webhook_route(user, membership, endpoint_id):
    data = request.get_json(silent=True) or {}
    delivery = enqueue_webhook(request.organization_id, endpoint_id, data.get('event_type', 'integration.test'), data.get('payload', {}))
    if not delivery:
        return jsonify({'error': 'Webhook endpoint not found'}), 404
    return jsonify({'id': delivery.id, 'event_type': delivery.event_type, 'status': delivery.status}), 201


@integrations_bp.get('/integrations/webhooks/<endpoint_id>/deliveries')
@organization_member_required({'owner', 'admin'})
def list_deliveries(user, membership, endpoint_id):
    endpoint = WebhookEndpoint.query.filter_by(id=endpoint_id, organization_id=request.organization_id).first()
    if not endpoint:
        return jsonify({'error': 'Webhook endpoint not found'}), 404
    deliveries = WebhookDelivery.query.filter_by(endpoint_id=endpoint.id, organization_id=request.organization_id).order_by(WebhookDelivery.created_at.desc()).all()
    return jsonify([{'id': item.id, 'event_type': item.event_type, 'status': item.status, 'attempt_count': item.attempt_count,
                     'response_status': item.response_status, 'error': item.error} for item in deliveries]), 200

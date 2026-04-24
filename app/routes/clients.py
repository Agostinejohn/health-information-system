from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.schemas.client import ClientSchema, EnrollSchema
from app.services.client_service import register_client, search_clients, get_client, enroll_client

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

client_schema = ClientSchema()
enroll_schema = EnrollSchema()

@clients_bp.route('', methods=['POST'])
@jwt_required()
def create():
    try:
        data = client_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    client = register_client(data['name'], data['age'])
    return jsonify(client.to_dict()), 201

@clients_bp.route('', methods=['GET'])
@jwt_required()
def search():
    name_query = request.args.get('name', '').strip()
    if not name_query:
        return jsonify({'error': 'name query param is required'}), 400

    clients = search_clients(name_query)
    return jsonify([c.to_dict() for c in clients]), 200

@clients_bp.route('/<client_id>', methods=['GET'])
@jwt_required()
def get_profile(client_id):
    client = get_client(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404

    return jsonify(client.to_dict(include_programs=True)), 200

@clients_bp.route('/<client_id>/enroll', methods=['POST'])
@jwt_required()
def enroll(client_id):
    try:
        data = enroll_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    client, result = enroll_client(client_id, data['program_ids'])
    if not client:
        return jsonify({'error': result}), 404

    return jsonify({
        'client': client.to_dict(include_programs=True),
        'enrollment_result': result
    }), 200

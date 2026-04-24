from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError
from app.schemas.program import ProgramSchema
from app.services.program_service import create_program, get_all_programs

programs_bp = Blueprint('programs', __name__, url_prefix='/programs')

program_schema = ProgramSchema()

@programs_bp.route('', methods=['POST'])
@jwt_required()
def create():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admins only'}), 403

    try:
        data = program_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    program, error = create_program(data['name'])
    if error:
        return jsonify({'error': error}), 409

    return jsonify(program.to_dict()), 201

@programs_bp.route('', methods=['GET'])
@jwt_required()
def list_programs():
    programs = get_all_programs()
    return jsonify([p.to_dict() for p in programs]), 200

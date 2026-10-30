from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.auth_context import organization_member_required
from app.schemas.program import ProgramSchema
from app.services.program_service import create_program, get_all_programs

programs_bp = Blueprint('programs', __name__, url_prefix='/programs')
program_schema = ProgramSchema()

@programs_bp.route('', methods=['POST'])
@organization_member_required({'owner', 'admin'})
def create(user, membership):
    try:
        data = program_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    program, error = create_program(data['name'], request.organization_id)
    if error:
        return jsonify({'error': error}), 409

    return jsonify(program.to_dict()), 201

@programs_bp.route('', methods=['GET'])
@organization_member_required()
def list_programs(user, membership):
    programs = get_all_programs(request.organization_id)
    return jsonify([p.to_dict() for p in programs]), 200

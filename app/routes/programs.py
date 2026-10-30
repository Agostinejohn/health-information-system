from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.authorization import organization_member_required
from app.schemas.program import ProgramSchema, UpdateProgramSchema
from app.services.program_service import create_program, get_all_programs, get_program, update_program

programs_bp = Blueprint('programs', __name__, url_prefix='/programs')
program_schema = ProgramSchema()
update_program_schema = UpdateProgramSchema()

@programs_bp.route('', methods=['POST'])
@organization_member_required({'owner', 'admin'})
def create(user, membership):
    try:
        data = program_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    fields = {key: value for key, value in data.items() if key != 'name'}
    program, error = create_program(data['name'], request.organization_id, **fields)
    if error:
        return jsonify({'error': error}), 409

    return jsonify(program.to_dict()), 201

@programs_bp.route('', methods=['GET'])
@organization_member_required()
def list_programs(user, membership):
    programs = get_all_programs(request.organization_id)
    return jsonify([p.to_dict() for p in programs]), 200

@programs_bp.route('/<program_id>', methods=['GET'])
@organization_member_required()
def get_program_detail(user, membership, program_id):
    program = get_program(program_id, request.organization_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404
    return jsonify(program.to_dict()), 200

@programs_bp.route('/<program_id>', methods=['PATCH'])
@organization_member_required({'owner', 'admin'})
def patch_program(user, membership, program_id):
    try:
        data = update_program_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    program = get_program(program_id, request.organization_id)
    if not program:
        return jsonify({'error': 'Program not found'}), 404
    program, error = update_program(program, data)
    if error:
        return jsonify({'error': error}), 409
    return jsonify(program.to_dict()), 200

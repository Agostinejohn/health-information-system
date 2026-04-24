from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from app.schemas.auth import RegisterSchema, LoginSchema
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

register_schema = RegisterSchema()
login_schema = LoginSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    user, error = register_user(data['email'], data['password'], data['role'])
    if error:
        return jsonify({'error': error}), 409

    return jsonify(user.to_dict()), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    user, error = login_user(data['email'], data['password'])
    if error:
        return jsonify({'error': error}), 401

    token = create_access_token(identity=user.id, additional_claims={'role': user.role})
    return jsonify({'access_token': token, 'user': user.to_dict()}), 200

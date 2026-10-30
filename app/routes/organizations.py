from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.authorization import current_user, organization_member_required
from app.schemas.organization import CreateOrganizationSchema, InviteMemberSchema, AcceptInvitationSchema
from app.services.organization_service import create_organization, list_user_organizations, invite_member, accept_invitation

organizations_bp = Blueprint('organizations', __name__, url_prefix='/organizations')
create_schema = CreateOrganizationSchema()
invite_schema = InviteMemberSchema()
accept_schema = AcceptInvitationSchema()


@organizations_bp.post('')
@jwt_required()
def create():
    try:
        data = create_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400

    organization, error = create_organization(data['name'], current_user())
    if error:
        return jsonify({'error': error}), 400
    return jsonify(organization.to_dict()), 201


@organizations_bp.get('')
@jwt_required()
def list_organizations():
    organizations = list_user_organizations(current_user().id)
    return jsonify([organization.to_dict() for organization in organizations]), 200


@organizations_bp.get('/<organization_id>')
@organization_member_required()
def get_organization(user, membership, organization_id):
    organization = membership.organization
    return jsonify(organization.to_dict()), 200


@organizations_bp.post('/<organization_id>/invitations')
@organization_member_required({'owner', 'admin'})
def invite(user, membership, organization_id):
    try:
        data = invite_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400

    result, error = invite_member(organization_id, user, data['email'], data['role'])
    if error:
        return jsonify({'error': error}), 409

    invitation = result['invitation']
    return jsonify({
        'id': invitation.id,
        'email': invitation.email,
        'role': invitation.role,
        'status': invitation.status,
        'invite_token': result['token'],
        'expires_at': invitation.expires_at.isoformat()
    }), 201


@organizations_bp.post('/invitations/accept')
@jwt_required()
def accept():
    try:
        data = accept_schema.load(request.get_json() or {})
    except ValidationError as error:
        return jsonify({'errors': error.messages}), 400

    membership, error = accept_invitation(data['token'], current_user())
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'organization_id': membership.organization_id, 'role': membership.role}), 200

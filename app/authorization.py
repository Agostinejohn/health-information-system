from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models.user import User
from app.models.organization import OrganizationMembership


def current_user():
    identity = get_jwt_identity()
    return db.session.get(User, identity)


def organization_member_required(allowed_roles=None):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapped(*args, **kwargs):
            organization_id = request.headers.get('X-Organization-ID')
            user = current_user()
            if not organization_id:
                return jsonify({'error': 'X-Organization-ID header is required'}), 400
            if not user:
                return jsonify({'error': 'User not found'}), 401

            membership = OrganizationMembership.query.filter_by(
                organization_id=organization_id,
                user_id=user.id,
                status='active'
            ).first()
            if not membership:
                return jsonify({'error': 'Organization membership required'}), 403
            if allowed_roles and membership.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403

            request.organization_id = organization_id
            request.organization_membership = membership
            return view(user, membership, *args, **kwargs)
        return wrapped
    return decorator

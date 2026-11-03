from flask import Flask
from sqlalchemy import text
from config import get_config, ProductionConfig
from app.db import db, migrate, jwt
from app.models import User, Program, Client, enrollments, Organization, OrganizationMembership, OrganizationInvitation
from app.routes.auth import auth_bp
from app.routes.clients import clients_bp
from app.routes.programs import programs_bp
from app.routes.organizations import organizations_bp
from app.routes.care_work import care_work_bp
from app.routes.service_delivery import service_delivery_bp
from app.routes.reports import reports_bp
from app.routes.integrations import integrations_bp
from app.routes.billing import billing_bp


def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(get_config())

    configured_class = config or get_config()
    if configured_class is ProductionConfig:
        ProductionConfig.validate(configured_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(programs_bp)
    app.register_blueprint(organizations_bp)
    app.register_blueprint(care_work_bp)
    app.register_blueprint(service_delivery_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(integrations_bp)
    app.register_blueprint(billing_bp)

    @app.get('/health/live')
    def liveness():
        return {'status': 'alive'}, 200

    @app.get('/health/ready')
    def readiness():
        try:
            with app.app_context():
                db.session.execute(text('SELECT 1'))
            return {'status': 'ready'}, 200
        except Exception:
            app.logger.exception('Database readiness check failed')
            return {'status': 'not_ready'}, 503

    @app.route('/')
    def health_check():
        return {
            'status': 'ok',
            'message': 'Health Information System API is running'
        }, 200

    return app

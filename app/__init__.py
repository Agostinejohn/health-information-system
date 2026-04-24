from flask import Flask
from config import get_config
from app.db import db, migrate, jwt
from app.models import User, Program, Client, enrollments
from app.routes.auth import auth_bp
from app.routes.clients import clients_bp
from app.routes.programs import programs_bp

def create_app(config=None):
    app = Flask(__name__)

    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(get_config())

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(programs_bp)

    @app.route('/')
    def health_check():
        return {'status': 'ok', 'message': 'Health Information System API is running'}, 200

    return app

import os
from dotenv import load_dotenv

load_dotenv()


def _get_db_url():
    url = os.getenv('DATABASE_URL', 'sqlite:///health.db')
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql+psycopg2://', 1)
    elif url.startswith('postgresql://'):
        url = url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    return url


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-prod')
    SQLALCHEMY_DATABASE_URI = _get_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-prod')
    JWT_ACCESS_TOKEN_EXPIRES = 3600


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    def validate(self):
        insecure_values = {
            'SECRET_KEY': ('dev-secret-change-in-prod',),
            'JWT_SECRET_KEY': ('jwt-secret-change-in-prod',),
        }
        missing = []
        for setting, defaults in insecure_values.items():
            value = getattr(self, setting, '')
            if not value or value in defaults or len(value) < 32:
                missing.append(setting)

        database_url = getattr(self, 'SQLALCHEMY_DATABASE_URI', '')
        if database_url.startswith('sqlite:'):
            missing.append('DATABASE_URL')

        if missing:
            raise RuntimeError(
                'Production configuration is incomplete or insecure: '
                + ', '.join(sorted(set(missing)))
            )


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig,
}


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)
from app.db import db
from app.models.user import User

def register_user(email: str, password: str, role: str) -> dict:
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered'
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, None

def login_user(email: str, password: str):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, 'Invalid email or password'
    return user, None

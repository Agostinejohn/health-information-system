import uuid
from app.db import db

enrollments = db.Table(
    'enrollments',
    db.Column('client_id', db.String(36), db.ForeignKey('clients.id'), primary_key=True),
    db.Column('program_id', db.String(36), db.ForeignKey('programs.id'), primary_key=True)
)

class Client(db.Model):
    __tablename__ = 'clients'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    external_reference = db.Column(db.String(100), nullable=True, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True)
    programs = db.relationship('Program', secondary=enrollments, backref='clients', lazy=True)

    def to_dict(self, include_programs=False):
        data = {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'external_reference': self.external_reference,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'status': self.status,
        }
        if include_programs:
            data['programs'] = [p.to_dict() for p in self.programs]
        return data


class ClientConsent(db.Model):
    __tablename__ = 'client_consents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    consent_type = db.Column(db.String(100), nullable=False)
    granted = db.Column(db.Boolean, nullable=False)
    note = db.Column(db.Text, nullable=True)
    recorded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    recorded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class ClientDocument(db.Model):
    __tablename__ = 'client_documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False, default='general')
    storage_key = db.Column(db.String(500), nullable=False)
    content_type = db.Column(db.String(100), nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class ClientTimelineEvent(db.Model):
    __tablename__ = 'client_timeline_events'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    event_type = db.Column(db.String(80), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    actor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

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
    programs = db.relationship('Program', secondary=enrollments, backref='clients', lazy=True)

    def to_dict(self, include_programs=False):
        data = {'id': self.id, 'name': self.name, 'age': self.age}
        if include_programs:
            data['programs'] = [p.to_dict() for p in self.programs]
        return data

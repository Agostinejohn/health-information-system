import uuid
from app.db import db

class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    capacity = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'name', name='uq_program_organization_name'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'capacity': self.capacity,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
        }


class ProgramEnrollment(db.Model):
    __tablename__ = 'program_enrollments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    enrolled_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    enrolled_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    ended_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('client_id', 'program_id', name='uq_client_program_enrollment'),
    )

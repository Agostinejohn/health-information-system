import uuid
from app.db import db

class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=True, index=True)

    __table_args__ = (
        db.UniqueConstraint('organization_id', 'name', name='uq_program_organization_name'),
    )

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

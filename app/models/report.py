import uuid
from app.db import db


class ReportExport(db.Model):
    __tablename__ = 'report_exports'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    requested_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    report_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ready')
    filters = db.Column(db.JSON, nullable=False, default=dict)
    file_name = db.Column(db.String(255), nullable=True)
    record_count = db.Column(db.Integer, nullable=False, default=0)
    requested_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)

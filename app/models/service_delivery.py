import uuid
from app.db import db


class AssessmentTemplate(db.Model):
    __tablename__ = 'assessment_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft')
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class AssessmentTemplateVersion(db.Model):
    __tablename__ = 'assessment_template_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = db.Column(db.String(36), db.ForeignKey('assessment_templates.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False)
    definition = db.Column(db.JSON, nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint('template_id', 'version_number', name='uq_template_version'),)


class ServiceDelivery(db.Model):
    __tablename__ = 'service_deliveries'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.String(36), db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    appointment_id = db.Column(db.String(36), db.ForeignKey('appointments.id', ondelete='SET NULL'), nullable=True, index=True)
    template_version_id = db.Column(db.String(36), db.ForeignKey('assessment_template_versions.id', ondelete='SET NULL'), nullable=True)
    service_type = db.Column(db.String(100), nullable=False)
    outcome = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    answers = db.Column(db.JSON, nullable=False, default=dict)
    status = db.Column(db.String(20), nullable=False, default='recorded')
    provided_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    recorded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    corrected_at = db.Column(db.DateTime, nullable=True)


class ServiceDeliveryCorrection(db.Model):
    __tablename__ = 'service_delivery_corrections'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_delivery_id = db.Column(db.String(36), db.ForeignKey('service_deliveries.id', ondelete='CASCADE'), nullable=False, index=True)
    organization_id = db.Column(db.String(36), db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True)
    corrected_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    previous_answers = db.Column(db.JSON, nullable=False)
    previous_notes = db.Column(db.Text, nullable=True)
    corrected_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

from datetime import datetime, timezone
from app.db import db
from app.models.client import Client
from app.models.program import Program
from app.models.service_delivery import (
    AssessmentTemplate, AssessmentTemplateVersion,
    ServiceDelivery, ServiceDeliveryCorrection
)


def _utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_template(organization_id, actor_id, data):
    if data.get('program_id') and not Program.query.filter_by(id=data['program_id'], organization_id=organization_id).first():
        return None, 'Program not found'

    template = AssessmentTemplate(
        organization_id=organization_id,
        program_id=data.get('program_id'),
        name=data['name'],
        description=data.get('description'),
        status='draft',
        created_by=actor_id
    )
    db.session.add(template)
    db.session.flush()

    version = AssessmentTemplateVersion(
        template_id=template.id,
        organization_id=organization_id,
        version_number=1,
        definition=data['definition'],
        created_by=actor_id
    )
    db.session.add(version)
    db.session.commit()
    return template, version, None


def create_service_delivery(organization_id, actor_id, data):
    client = Client.query.filter_by(id=data['client_id'], organization_id=organization_id, status='active').first()
    if not client:
        return None, 'Client not found'
    if data.get('program_id') and not Program.query.filter_by(id=data['program_id'], organization_id=organization_id).first():
        return None, 'Program not found'
    if data.get('template_version_id'):
        version = AssessmentTemplateVersion.query.filter_by(id=data['template_version_id'], organization_id=organization_id).first()
        if not version:
            return None, 'Assessment template version not found'

    delivery = ServiceDelivery(
        organization_id=organization_id,
        provided_by=actor_id,
        status='recorded',
        **data
    )
    db.session.add(delivery)
    db.session.flush()

    from app.models.client import ClientTimelineEvent
    timeline = ClientTimelineEvent(
        client_id=client.id,
        organization_id=organization_id,
        event_type='service_delivery',
        title=data['service_type'],
        description=data.get('notes'),
        actor_id=actor_id
    )
    db.session.add(timeline)
    db.session.commit()
    return delivery, None


def correct_service_delivery(delivery, organization_id, actor_id, data):
    correction = ServiceDeliveryCorrection(
        service_delivery_id=delivery.id,
        organization_id=organization_id,
        corrected_by=actor_id,
        reason=data['reason'],
        previous_answers=delivery.answers.copy() if delivery.answers else {},
        previous_notes=delivery.notes
    )
    delivery.answers = data['answers']
    delivery.notes = data.get('notes', delivery.notes)
    delivery.outcome = data.get('outcome', delivery.outcome)
    delivery.status = 'corrected'
    delivery.corrected_at = _utc_now()
    db.session.add(correction)
    db.session.commit()
    return delivery, correction

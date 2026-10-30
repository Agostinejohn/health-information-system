from datetime import datetime, timezone
from app.db import db
from app.models.client import Client, ClientConsent, ClientDocument, ClientTimelineEvent
from app.models.program import Program, ProgramEnrollment


def register_client(name: str, age: int, organization_id: str, **fields):
    client = Client(name=name, age=age, organization_id=organization_id, **fields)
    db.session.add(client)
    db.session.flush()

    event = ClientTimelineEvent(
        client_id=client.id,
        organization_id=organization_id,
        event_type='registration',
        title='Client registered',
        actor_id=None
    )
    db.session.add(event)
    db.session.commit()
    return client


def search_clients(name_query: str, organization_id: str):
    return Client.query.filter(
        Client.organization_id == organization_id,
        Client.name.ilike(f'%{name_query}%'),
        Client.status == 'active'
    ).all()


def find_duplicate_candidates(name, organization_id, email=None, phone=None, external_reference=None, client_id=None):
    query = Client.query.filter_by(organization_id=organization_id, status='active')
    if client_id:
        query = query.filter(Client.id != client_id)

    candidates = []
    normalized_name = name.strip().casefold()
    for candidate in query.all():
        if candidate.name.strip().casefold() == normalized_name:
            candidates.append(candidate)
            continue
        if email and candidate.email and candidate.email.casefold() == email.strip().casefold():
            candidates.append(candidate)
            continue
        if phone and candidate.phone and candidate.phone.strip() == phone.strip():
            candidates.append(candidate)
            continue
        if external_reference and candidate.external_reference and candidate.external_reference == external_reference:
            candidates.append(candidate)
    return candidates


def get_client(client_id: str, organization_id: str):
    return Client.query.filter_by(id=client_id, organization_id=organization_id, status='active').first()


def record_consent(client_id: str, organization_id: str, user_id: str, **fields):
    if not get_client(client_id, organization_id):
        return None
    consent = ClientConsent(client_id=client_id, organization_id=organization_id, recorded_by=user_id, **fields)
    db.session.add(consent)
    db.session.commit()
    return consent


def record_document(client_id: str, organization_id: str, user_id: str, **fields):
    if not get_client(client_id, organization_id):
        return None
    document = ClientDocument(client_id=client_id, organization_id=organization_id, uploaded_by=user_id, **fields)
    db.session.add(document)
    db.session.commit()
    return document


def get_client_timeline(client_id: str, organization_id: str):
    if not get_client(client_id, organization_id):
        return None
    return ClientTimelineEvent.query.filter_by(client_id=client_id, organization_id=organization_id).order_by(ClientTimelineEvent.created_at.desc()).all()


def enroll_client(client_id: str, program_ids: list, organization_id: str, user_id: str = None):
    client = Client.query.filter_by(id=client_id, organization_id=organization_id, status='active').first()
    if not client:
        return None, 'Client not found'

    enrolled = []
    reactivated = []
    not_found = []

    for program_id in program_ids:
        program = Program.query.filter_by(id=program_id, organization_id=organization_id).first()
        if not program:
            not_found.append(program_id)
            continue
        if program.status != 'active':
            continue

        active_count = ProgramEnrollment.query.filter_by(program_id=program.id, status='active').count()
        if program.capacity and active_count >= program.capacity:
            continue

        enrollment = ProgramEnrollment.query.filter_by(client_id=client.id, program_id=program.id).first()
        if enrollment:
            if enrollment.status == 'active':
                continue
            enrollment.status = 'active'
            enrollment.ended_at = None
            enrollment.enrolled_by = user_id
            if program not in client.programs:
                client.programs.append(program)
            reactivated.append(program.name)
        else:
            enrollment = ProgramEnrollment(
                client_id=client.id,
                program_id=program.id,
                organization_id=organization_id,
                status='active',
                enrolled_by=user_id
            )
            db.session.add(enrollment)
            if program not in client.programs:
                client.programs.append(program)
            enrolled.append(program.name)

    db.session.commit()
    return client, {
        'enrolled': enrolled,
        'reactivated': reactivated,
        'not_found': not_found
    }


def update_enrollment_status(client_id: str, program_id: str, organization_id: str, status: str, reason: str = None):
    enrollment = ProgramEnrollment.query.filter_by(
        client_id=client_id,
        program_id=program_id,
        organization_id=organization_id
    ).first()
    if not enrollment:
        return None
    enrollment.status = status
    enrollment.reason = reason
    enrollment.ended_at = datetime.now(timezone.utc).replace(tzinfo=None)
    if status != 'active':
        program = db.session.get(Program, program_id)
        client = db.session.get(Client, client_id)
        if program in client.programs:
            client.programs.remove(program)
    db.session.commit()
    return enrollment

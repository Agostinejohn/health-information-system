from datetime import datetime, timezone
from io import StringIO
import csv
from app.db import db
from app.models.client import Client
from app.models.program import Program, ProgramEnrollment
from app.models.care_work import Appointment, FollowUp, Referral
from app.models.service_delivery import ServiceDelivery, ServiceDeliveryCorrection
from app.models.report import ReportExport


def _utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_dashboard(organization_id, program_id=None):
    clients_query = Client.query.filter_by(organization_id=organization_id, status='active')
    enrollments_query = ProgramEnrollment.query.filter_by(organization_id=organization_id, status='active')
    appointments_query = Appointment.query.filter_by(organization_id=organization_id)
    followups_query = FollowUp.query.filter_by(organization_id=organization_id)
    referrals_query = Referral.query.filter_by(organization_id=organization_id)
    deliveries_query = ServiceDelivery.query.filter_by(organization_id=organization_id)

    if program_id:
        enrollments_query = enrollments_query.filter_by(program_id=program_id)
        appointments_query = appointments_query.filter_by(program_id=program_id)
        followups_query = followups_query.filter_by(program_id=program_id)
        referrals_query = referrals_query.filter_by(program_id=program_id)
        deliveries_query = deliveries_query.filter_by(program_id=program_id)

    return {
        'active_clients': clients_query.count(),
        'active_enrollments': enrollments_query.count(),
        'upcoming_appointments': appointments_query.filter(Appointment.status.in_(['scheduled', 'confirmed']), Appointment.scheduled_at >= _utc_now()).count(),
        'overdue_follow_ups': followups_query.filter(FollowUp.status.in_(['pending', 'in_progress']), FollowUp.due_at < _utc_now()).count(),
        'open_referrals': referrals_query.filter(Referral.status.in_(['referred', 'accepted'])).count(),
        'service_deliveries': deliveries_query.count(),
        'corrected_service_deliveries': ServiceDelivery.query.filter_by(organization_id=organization_id, status='corrected').count()
    }


def get_program_summary(organization_id):
    programs = Program.query.filter_by(organization_id=organization_id).order_by(Program.name).all()
    result = []
    for program in programs:
        active_enrollments = ProgramEnrollment.query.filter_by(organization_id=organization_id, program_id=program.id, status='active').count()
        deliveries = ServiceDelivery.query.filter_by(organization_id=organization_id, program_id=program.id).count()
        overdue_followups = FollowUp.query.filter_by(organization_id=organization_id, program_id=program.id).filter(FollowUp.status.in_(['pending', 'in_progress']), FollowUp.due_at < _utc_now()).count()
        result.append({
            'program_id': program.id,
            'name': program.name,
            'status': program.status,
            'capacity': program.capacity,
            'active_enrollments': active_enrollments,
            'service_deliveries': deliveries,
            'overdue_follow_ups': overdue_followups
        })
    return result


def generate_report_csv(organization_id, report_type, filters=None):
    filters = filters or {}
    if report_type == 'clients':
        rows = Client.query.filter_by(organization_id=organization_id, status='active')
        records = [{'id': item.id, 'name': item.name, 'age': item.age, 'email': item.email, 'phone': item.phone} for item in rows.all()]
        fieldnames = ['id', 'name', 'age', 'email', 'phone']
    elif report_type == 'enrollments':
        rows = ProgramEnrollment.query.filter_by(organization_id=organization_id)
        records = [{'id': item.id, 'client_id': item.client_id, 'program_id': item.program_id, 'status': item.status, 'enrolled_at': item.enrolled_at.isoformat()} for item in rows.all()]
        fieldnames = ['id', 'client_id', 'program_id', 'status', 'enrolled_at']
    elif report_type == 'service-deliveries':
        rows = ServiceDelivery.query.filter_by(organization_id=organization_id)
        records = [{'id': item.id, 'client_id': item.client_id, 'program_id': item.program_id, 'service_type': item.service_type, 'outcome': item.outcome, 'status': item.status} for item in rows.all()]
        fieldnames = ['id', 'client_id', 'program_id', 'service_type', 'outcome', 'status']
    else:
        return None, None, 'Unsupported report type'

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)
    return records, output.getvalue(), None


def create_export(organization_id, actor_id, report_type, filters=None):
    filters = filters or {}
    records, csv_content, error = generate_report_csv(organization_id, report_type, filters)
    if error:
        return None, error

    export = ReportExport(organization_id=organization_id, requested_by=actor_id, report_type=report_type,
                         status='ready', filters=filters, record_count=len(records))
    db.session.add(export)
    db.session.flush()
    export.file_name = f'{report_type}-{export.id}.csv'
    db.session.commit()
    return {'export': export, 'csv': csv_content}, None

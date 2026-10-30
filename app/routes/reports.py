from flask import Blueprint, request, jsonify, Response
from app.authorization import organization_member_required
from app.services.report_service import get_dashboard, get_program_summary, create_export, generate_report_csv

reports_bp = Blueprint('reports', __name__)


@reports_bp.get('/reports/dashboard')
@organization_member_required()
def dashboard(user, membership):
    return jsonify(get_dashboard(request.organization_id, request.args.get('program_id'))), 200


@reports_bp.get('/reports/programs')
@organization_member_required()
def program_summary(user, membership):
    return jsonify(get_program_summary(request.organization_id)), 200


@reports_bp.post('/reports/exports')
@organization_member_required({'owner', 'admin', 'manager'})
def export_report(user, membership):
    data = request.get_json(silent=True) or {}
    report_type = data.get('report_type')
    if report_type not in {'clients', 'enrollments', 'service-deliveries'}:
        return jsonify({'error': 'Unsupported report type'}), 400

    result, error = create_export(request.organization_id, user.id, report_type, data.get('filters'))
    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'id': result['export'].id,
        'report_type': result['export'].report_type,
        'status': result['export'].status,
        'file_name': result['export'].file_name,
        'record_count': result['export'].record_count,
        'csv': result['csv']
    }), 201


@reports_bp.get('/reports/exports/<export_id>/csv')
@organization_member_required({'owner', 'admin', 'manager'})
def download_export(user, membership, export_id):
    from app.models.report import ReportExport
    export = ReportExport.query.filter_by(id=export_id, organization_id=request.organization_id).first()
    if not export:
        return jsonify({'error': 'Report export not found'}), 404

    records, csv_content, error = generate_report_csv(request.organization_id, export.report_type, export.filters)
    if error:
        return jsonify({'error': error}), 400
    return Response(csv_content, mimetype='text/csv', headers={
        'Content-Disposition': f"attachment; filename={export.file_name or export.report_type + '.csv'}"
    })

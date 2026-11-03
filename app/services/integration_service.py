import csv
import hashlib
import secrets
from io import StringIO
from datetime import datetime, timezone
from app.db import db
from app.models.client import Client
from app.models.integration import IntegrationCredential, IdempotencyRecord, WebhookEndpoint, WebhookDelivery


def preview_client_import(organization_id, rows):
    preview = []
    errors = []
    for index, row in enumerate(rows, start=1):
        name = str(row.get('name', '')).strip()
        try:
            age = int(row.get('age'))
        except (TypeError, ValueError):
            age = None
        item_errors = []
        if not name:
            item_errors.append('name is required')
        if age is None or age < 0 or age > 150:
            item_errors.append('age must be between 0 and 150')
        duplicate = name and Client.query.filter_by(organization_id=organization_id, status='active').filter(db.func.lower(Client.name) == name.lower()).first()
        if duplicate:
            item_errors.append('possible duplicate')
        preview.append({'row': index, 'name': name, 'age': age, 'valid': not item_errors})
        if item_errors:
            errors.append({'row': index, 'errors': item_errors})
    return {'total': len(rows), 'valid': len(rows) - len(errors), 'invalid': len(errors), 'rows': preview, 'errors': errors}


def commit_client_import(organization_id, rows):
    preview = preview_client_import(organization_id, rows)
    created = []
    if preview['invalid']:
        return None, 'Import contains invalid or duplicate rows'
    for row in rows:
        client = Client(name=str(row['name']).strip(), age=int(row['age']), organization_id=organization_id,
                        external_reference=row.get('external_reference') or None,
                        email=row.get('email') or None, phone=row.get('phone') or None,
                        address=row.get('address') or None)
        db.session.add(client)
        db.session.flush()
        created.append(client.id)
    db.session.commit()
    return {'created': len(created), 'client_ids': created}, None


def create_api_credential(organization_id, actor_id, name):
    raw_key = 'his_' + secrets.token_urlsafe(32)
    prefix = raw_key[:12]
    credential = IntegrationCredential(organization_id=organization_id, created_by=actor_id, name=name,
                                       key_prefix=prefix, key_hash=hashlib.sha256(raw_key.encode()).hexdigest())
    db.session.add(credential)
    db.session.commit()
    return credential, raw_key


def revoke_api_credential(credential):
    credential.status = 'revoked'
    credential.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.session.commit()


def create_webhook(organization_id, name, url):
    raw_secret = secrets.token_urlsafe(32)
    webhook = WebhookEndpoint(organization_id=organization_id, name=name, url=url,
                              secret_hash=hashlib.sha256(raw_secret.encode()).hexdigest())
    db.session.add(webhook)
    db.session.commit()
    return webhook, raw_secret


def enqueue_webhook(organization_id, endpoint_id, event_type, payload):
    endpoint = WebhookEndpoint.query.filter_by(id=endpoint_id, organization_id=organization_id, status='active').first()
    if not endpoint:
        return None
    delivery = WebhookDelivery(endpoint_id=endpoint.id, organization_id=organization_id,
                               event_type=event_type, payload=payload, status='pending')
    db.session.add(delivery)
    db.session.commit()
    return delivery


def get_idempotent_response(organization_id, idempotency_key, request_path, request_hash):
    if not idempotency_key:
        return None
    record = IdempotencyRecord.query.filter_by(organization_id=organization_id,
                                               idempotency_key=idempotency_key,
                                               request_path=request_path).first()
    if record and record.request_hash != request_hash:
        raise ValueError('Idempotency key was already used with a different request')
    return record


def save_idempotent_response(organization_id, idempotency_key, request_path, request_hash, status, body):
    if not idempotency_key:
        return
    record = IdempotencyRecord(organization_id=organization_id, idempotency_key=idempotency_key,
                               request_path=request_path, request_hash=request_hash,
                               response_status=status, response_body=body)
    db.session.add(record)
    db.session.commit()

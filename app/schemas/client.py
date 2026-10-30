from marshmallow import Schema, fields, validate

class ClientSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=0, max=150))
    external_reference = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    email = fields.Email(load_default=None, allow_none=True)
    phone = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=30))
    address = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=255))


class ConsentSchema(Schema):
    consent_type = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    granted = fields.Bool(required=True)
    note = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2000))


class ClientDocumentSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    category = fields.Str(load_default='general', validate=validate.Length(min=1, max=80))
    storage_key = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    content_type = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))


class EnrollSchema(Schema):
    program_ids = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))

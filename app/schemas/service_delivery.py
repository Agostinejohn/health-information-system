from marshmallow import Schema, fields, validate


class AssessmentTemplateSchema(Schema):
    program_id = fields.Str(load_default=None, allow_none=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    description = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=4000))
    definition = fields.Dict(required=True)


class ServiceDeliverySchema(Schema):
    client_id = fields.Str(required=True)
    program_id = fields.Str(load_default=None, allow_none=True)
    appointment_id = fields.Str(load_default=None, allow_none=True)
    template_version_id = fields.Str(load_default=None, allow_none=True)
    service_type = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    outcome = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=8000))
    answers = fields.Dict(load_default=dict)


class ServiceDeliveryCorrectionSchema(Schema):
    reason = fields.Str(required=True, validate=validate.Length(min=3, max=4000))
    outcome = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=100))
    notes = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=8000))
    answers = fields.Dict(required=True)

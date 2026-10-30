from marshmallow import Schema, fields, validate

class ProgramSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    status = fields.Str(load_default='active', validate=validate.OneOf(['draft', 'active', 'paused', 'completed', 'archived']))
    capacity = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1, max=1000000))
    start_date = fields.Date(load_default=None, allow_none=True)
    end_date = fields.Date(load_default=None, allow_none=True)


class UpdateProgramSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True, validate=validate.Length(max=2000))
    status = fields.Str(validate=validate.OneOf(['draft', 'active', 'paused', 'completed', 'archived']))
    capacity = fields.Int(allow_none=True, validate=validate.Range(min=1, max=1000000))
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)


class EnrollmentStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['completed', 'withdrawn', 'ineligible', 'transferred', 'suspended']))
    reason = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2000))

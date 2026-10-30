from marshmallow import Schema, fields, validate


class AppointmentSchema(Schema):
    client_id = fields.Str(required=True)
    program_id = fields.Str(load_default=None, allow_none=True)
    assigned_to = fields.Str(load_default=None, allow_none=True)
    scheduled_at = fields.DateTime(required=True)
    timezone = fields.Str(load_default='UTC', validate=validate.Length(min=2, max=50))
    reason = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=255))
    notes = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=4000))


class AppointmentStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show']))
    notes = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=4000))


class FollowUpSchema(Schema):
    client_id = fields.Str(required=True)
    program_id = fields.Str(load_default=None, allow_none=True)
    assigned_to = fields.Str(load_default=None, allow_none=True)
    due_at = fields.DateTime(required=True)
    priority = fields.Str(load_default='normal', validate=validate.OneOf(['low', 'normal', 'high', 'urgent']))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    description = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=4000))


class FollowUpStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['pending', 'in_progress', 'completed', 'cancelled']))


class ReferralSchema(Schema):
    client_id = fields.Str(required=True)
    program_id = fields.Str(load_default=None, allow_none=True)
    destination = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    reason = fields.Str(required=True, validate=validate.Length(min=1, max=4000))
    priority = fields.Str(load_default='normal', validate=validate.OneOf(['low', 'normal', 'high', 'urgent']))


class ReferralStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['referred', 'accepted', 'completed', 'declined', 'cancelled']))
    outcome = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=4000))

from marshmallow import Schema, fields, validate


class SubscriptionPlanSchema(Schema):
    code = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    monthly_price = fields.Decimal(required=True, places=2, as_string=True, validate=validate.Range(min=0))
    currency = fields.Str(load_default='USD', validate=validate.Length(equal=3))
    max_users = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1))
    max_clients = fields.Int(load_default=None, allow_none=True, validate=validate.Range(min=1))
    entitlements = fields.Dict(load_default=dict)


class SubscriptionChangeSchema(Schema):
    plan_code = fields.Str(required=True, validate=validate.Length(min=1, max=50))


class InvoiceStatusSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(['draft', 'open', 'paid', 'void']))
    provider_invoice_id = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=255))


class SubscriptionLifecycleSchema(Schema):
    action = fields.Str(required=True, validate=validate.OneOf(['cancel', 'restore', 'suspend']))
    reason = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=2000))

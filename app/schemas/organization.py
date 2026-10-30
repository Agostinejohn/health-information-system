from marshmallow import Schema, fields, validate


class CreateOrganizationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=120))


class InviteMemberSchema(Schema):
    email = fields.Email(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(['admin', 'manager', 'doctor', 'staff']))


class AcceptInvitationSchema(Schema):
    token = fields.Str(required=True, validate=validate.Length(min=20, max=200))

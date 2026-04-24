from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6, max=128))
    role = fields.Str(load_default='doctor', validate=validate.OneOf(['admin', 'doctor']))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

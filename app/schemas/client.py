from marshmallow import Schema, fields, validate

class ClientSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=0, max=150))

class EnrollSchema(Schema):
    program_ids = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))

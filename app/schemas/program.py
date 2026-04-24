from marshmallow import Schema, fields, validate

class ProgramSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))

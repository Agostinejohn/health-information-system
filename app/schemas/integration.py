from marshmallow import Schema, fields, validate


class ImportClientsSchema(Schema):
    rows = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1, max=1000))


class CreateWebhookSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    url = fields.Url(required=True, schemes={'http', 'https'})


class IntegrationCredentialSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))

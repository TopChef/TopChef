from marshmallow import Schema, fields


class JSONSchemaValidator(Schema):
    """
    Describes the form for a validator
    """
    instance = fields.Dict(required=True)
    schema = fields.Dict(required=True)

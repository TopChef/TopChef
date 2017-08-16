from marshmallow import Schema, fields


class NewJobSchema(Schema):
    parameters = fields.Dict(required=True)

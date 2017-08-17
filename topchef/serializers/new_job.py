from marshmallow import Schema, fields


class NewJob(Schema):
    parameters = fields.Dict(required=True)

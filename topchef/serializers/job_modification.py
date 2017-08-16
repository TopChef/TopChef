from marshmallow import Schema, fields
from .custom_fields import JobStatusField


class JobModification(Schema):
    status = JobStatusField(required=True)
    results = fields.Dict(required=True)

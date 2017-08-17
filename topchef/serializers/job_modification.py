from marshmallow import Schema, fields
from .custom_fields import JobStatusField


class JobModification(Schema):
    status = JobStatusField(required=False)
    results = fields.Dict(required=False)

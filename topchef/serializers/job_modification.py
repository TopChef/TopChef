from marshmallow import Schema, fields
from .custom_fields import JobStatusField


class JobModification(Schema):
    status = JobStatusField(required=False, allow_none=True)
    results = fields.Dict(required=False, allow_none=True)

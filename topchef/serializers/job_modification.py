"""
Describes a ``PATCH`` request sent in to modify job parameters
"""
from marshmallow import Schema, fields
from .custom_fields import JobStatusField


class JobModification(Schema):
    """
    The schema that must be satisfied for a valid request to change the job
    parameters
    """
    status = JobStatusField(required=False, allow_none=True)
    results = fields.Dict(required=False, allow_none=True)

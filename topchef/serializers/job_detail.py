"""
Contains a serializer for printing all information about a job
"""
from marshmallow import Schema, fields
from topchef.serializers.custom_fields import JobStatusField


class JobDetail(Schema):
    id = fields.UUID(required=True)
    status = JobStatusField(required=True)
    parameters = fields.Dict(required=True)
    results = fields.Dict(required=True)
    date_submitted = fields.DateTime()

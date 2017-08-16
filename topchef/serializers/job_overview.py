"""
Contains a serializer for rough serialization of jobs
"""
from marshmallow import Schema, fields
from topchef.serializers.custom_fields.job_status_field import JobStatusField


class JobOverview(Schema):
    """
    Describes an overview schema for serializing general information about jobs
    """
    id = fields.UUID(dump_only=True, required=True)
    status = JobStatusField(dump_only=True, required=True)
    date_submitted = fields.DateTime(dump_only=True, required=True)

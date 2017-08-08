"""
Contains a serializer that can output detailed information related to a service
"""
from marshmallow import Schema, fields
from topchef.serializers.job_overview import JobOverview


class ServiceDetail(Schema):
    """
    A detailed serializer for services
    """
    id = fields.UUID(required=True, dump_only=True)
    name = fields.Str(required=True, dump_only=True)
    description = fields.Str(required=True, dump_only=True)
    job_registration_schema = fields.Dict(required=True, dump_only=True)
    job_result_schema = fields.Dict(required=True, dump_only=True)
    is_service_available = fields.Boolean(required=True, dump_only=True)
    jobs = fields.Nested(JobOverview, required=False, dump_only=True,
                         many=True, allow_none=True)

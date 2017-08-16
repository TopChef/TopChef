"""
Describes a serializer that can be used to create a new service
"""
from marshmallow import Schema, fields


class NewService(Schema):
    """
    The marshmallow schema containing the fields to be filled out in order
    to create a new service
    """
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    job_registration_schema = fields.Dict(required=True)
    job_result_schema = fields.Dict(required=True)

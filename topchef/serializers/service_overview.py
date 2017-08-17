"""
Contains a serializer that takes in a ``Service``, and outputs a small
representation of it as JSON
"""
from marshmallow import Schema, fields


class ServiceOverview(Schema):
    """
    Describes the serializer
    """
    id = fields.UUID(dump_only=True, required=True)
    name = fields.Str(dump_only=True, required=True)
    description = fields.Str(dump_only=True, required=True)

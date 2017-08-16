"""
Contains a serializer for dumping API exceptions
"""
from marshmallow import Schema, fields


class APIException(Schema):
    """
    Describes the serializer
    """
    status_code = fields.Int(dump_only=True, required=True)
    title = fields.Str(dump_only=True, required=True)
    detail = fields.Str(dump_only=True, required=True)

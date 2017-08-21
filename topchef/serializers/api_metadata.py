"""
Contains a serializer for displaying metadata relevant to properly running
this API
"""
from marshmallow import Schema
from marshmallow import fields


class APIMetadata(Schema):
    """
    Outputs fields corresponding to API metadata
    """
    maintainer_name = fields.Str(dump_only=True, required=True)
    maintainer_email = fields.Email(dump_only=True, required=True)
    documentation_url = fields.URL(dump_only=True, required=True)
    source_code_repository_url = fields.URL(dump_only=True, required=True)
    version = fields.Str(dump_only=True, required=True)

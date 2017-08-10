"""
Contains a serializer that can output detailed information related to a service
"""
from marshmallow import Schema, fields
from marshmallow_jsonschema import JSONSchema
from topchef.serializers.job_overview import JobOverview
from typing import Type, Iterable, Any


class _IterableField(fields.Field):
    def __init__(self, schema_class: Type[Schema], *args, **kwargs) -> None:
        super(_IterableField, self).__init__(*args, **kwargs)
        self._schema = schema_class()

    def _serialize(self, value: Iterable[Any], attr, obj):
        return [self._schema.dump(item).data for item in value]

    def _deserialize(self, value: Iterable[dict], attr, data):
        return [self._schema.load(item).data for item in value]

    def _jsonschema_type_mapping(self) -> dict:
        return {
            'type': 'array',
            'items': JSONSchema().dump(self).data
        }


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
    jobs = _IterableField(JobOverview)

from typing import Type, Iterable, Any

from marshmallow import fields, Schema
from marshmallow_jsonschema import JSONSchema


class IterableField(fields.Field):
    def __init__(self, schema_class: Type[Schema], *args, **kwargs) -> None:
        super(IterableField, self).__init__(*args, **kwargs)
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
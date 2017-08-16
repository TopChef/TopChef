from marshmallow_jsonschema import JSONSchema as _MarshmallowJSONSchema
from marshmallow import Schema
from typing import Optional
from topchef.json_type import JSON_TYPE as JSON


class JSONSchema(object):
    def __init__(
            self, schema="http://json-schema.org/draft-04/schema#",
            title: Optional[str]=None,
            description: Optional[str]=None,
            json_schema_serializer:
            _MarshmallowJSONSchema=_MarshmallowJSONSchema(strict=True)
    ):
        self._json_schema_serializer = json_schema_serializer
        self.schema = schema
        self.title = title
        self.description = description

    def dump(self, schema: Schema, many=False) -> JSON:
        result = self._json_schema_serializer.dump(schema, many=many).data
        self._add_title(result)
        self._add_description(result)
        self._add_schema(result)

        return result

    def dumps(self, schema: Schema, many=False) -> str:
        return str(self.dump(schema, many=many))

    def _add_title(self, result: JSON) -> None:
        if self.title is not None:
            result['title'] = self.title

    def _add_description(self, result: JSON) -> None:
        if self.description is not None:
            result['description'] = self.description

    def _add_schema(self, result: JSON):
        if self.schema is not None:
            result['$schema'] = self.schema

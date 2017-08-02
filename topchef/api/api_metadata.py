from flask_restful import Resource
from flask import jsonify
from topchef.serializers import APIMetadata as MetadataSerializer
from topchef.serializers import JSONSchema
from topchef.models.api_metadata import APIMetadata as MetadataModel


class APIMetadata(Resource):
    def get(self):
        response = jsonify({
            'data': self._data, 'meta': self._meta
        })
        response.status_code = 200
        return response

    @property
    def _data(self) -> dict:
        metadata_model = MetadataModel()
        serializer = MetadataSerializer(strict=True)
        return serializer.dump(metadata_model, many=False).data

    @property
    def _meta(self) -> dict:
        serializer = MetadataSerializer(strict=True)
        json_schema_serializer = JSONSchema(
            title=self.metadata_schema_title,
            description=self.metadata_schema_description
        )
        return {
            'schema': json_schema_serializer.dump(serializer, many=False)
        }

    @property
    def metadata_schema_title(self) -> str:
        return 'API Metadata'

    @property
    def metadata_schema_description(self) -> str:
        return 'Describes the JSON schema for describing API metadata'

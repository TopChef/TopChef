"""
Maps the ``/validator`` endpoint
"""
from .abstract_endpoints import AbstractEndpoint
from flask import Response, jsonify
from topchef.serializers import JSONSchema
from topchef.serializers import JSONSchemaValidator as ValidatorSerializer
from topchef.models.errors import DeserializationError
from topchef.models.errors import ValidationError as ReportableValidationError
from typing import Iterable
import jsonschema


class JSONSchemaValidator(AbstractEndpoint):
    """
    Maps an endpoint for validating objects against JSON Schemas
    """
    def get(self) -> Response:
        """

        :return: A flask response indicating how this validator is to be used
        """
        return jsonify({
            'data': {},
            'links': self.links,
            'meta': {
                'validator_schema': self.validator_schema
            }
        })

    def post(self) -> Response:
        """

        :return: A flask response indicating whether validation was
            successful or not
        """
        serializer = ValidatorSerializer()

        data, errors = serializer.load(self.request_json)

        if errors:
            self._report_deserialization_errors(errors)
            raise self.Abort()

        json_schema_validator = jsonschema.Draft4Validator(data['schema'])

        if not json_schema_validator.is_valid(data['instance']):
            self._report_validation_errors(
                json_schema_validator.iter_errors(data['instance'])
            )
            raise self.Abort()

        response = Response()
        response.status_code = 200
        return response

    @property
    def validator_schema(self) -> dict:
        """

        :return: The validator schema
        """
        schema_serializer = JSONSchema(
            title='JSON Schema Validator',
            description='The schema that must be satisfied in order to '
                        'validate an instance against a schema'
        )
        return schema_serializer.dump(ValidatorSerializer())

    def _report_deserialization_errors(self, errors: dict):
        self.errors.extend(
            (DeserializationError(key, errors[key]) for key in errors.keys())
        )

    def _report_validation_errors(
            self, errors: Iterable[jsonschema.ValidationError]
    ) -> None:
        self.errors.extend(
            ReportableValidationError(error) for error in errors
        )

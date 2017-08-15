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
        Return a schema indicating how the endpoint is to be used. The
        ``validator_schema`` keyword contains a JSON schema that must be
        satisified in order to ``POST`` requests to the API

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {},
                "links": {
                    "self": "http://localhost:5000/validator"
                },
                "meta": {
                    "validator_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The POST request schema",
                        "properties": {
                            "object": {
                                "title": "object",
                                "type": "object"
                            },
                            "schema": {
                                "title": "schema",
                                "type": "object"
                            }
                        },
                        "required": [
                            "object",
                            "schema"
                        ],
                        "title": "JSON Schema Validator",
                        "type": "object"
                    }
                }
            }

        :statuscode 200: The request completed successfully
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
        If a JSON schema validator cannot be found for the client side,
        use this method to validate against the server side

        **Example Request**

        .. sourcecode:: http

            POST /validator HTTP/1.1
            Content-Type: application/json

            {
                "schema": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "Validator Schema",
                    "description":
                        "A schema used for documenting this endpoit",
                    "type": "object",
                    "properties": {
                        "value": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        }
                    }
                },
                "object": {
                    "value": 1
                }
            }

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "status": "Validation was successful"
                },
                "links": {
                    "self": "http://localhost:5000/validator"
                }
            }

        :statuscode 200: The Validation completed successfully. The provided
            JSON object is an instance of the provided JSON Schema
        :statuscode 400: The validation was not successful. This may be due
            to the request not being correct JSON, or to the object not
            matching the schema. The ``errors`` object returned in this
            response will contain more information related to the error

        :return: A flask response indicating whether validation was
            successful or not
        """
        serializer = ValidatorSerializer()

        data, errors = serializer.load(self.request_json)

        if errors:
            self._report_deserialization_errors(errors)
            raise self.Abort()

        json_schema_validator = jsonschema.Draft4Validator(data['schema'])

        if not json_schema_validator.is_valid(data['object']):
            self._report_validation_errors(
                json_schema_validator.iter_errors(data['object'])
            )
            raise self.Abort()

        response = jsonify({
            'data': {
                'status': 'Validation was successful'
            },
            'links': self.links
        })
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

    def _report_deserialization_errors(self, errors: dict) -> None:
        """

        :param errors: The errors returned from Marshmallow
        """
        self.errors.extend(
            (DeserializationError(key, errors[key]) for key in errors.keys())
        )

    def _report_validation_errors(
            self, errors: Iterable[jsonschema.ValidationError]
    ) -> None:
        """

        :param errors: The validation errors returned from JSONSchema
        """
        self.errors.extend(
            ReportableValidationError(error) for error in errors
        )

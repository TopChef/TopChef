"""
Describes an endpoint where detailed information about the service can be
obtained
"""
from datetime import datetime
from flask import Response, jsonify
from topchef.api.abstract_endpoints import AbstractEndpointForService
from topchef.api.abstract_endpoints import AbstractEndpointForServiceMeta
from topchef.models import Service
from topchef.models.errors import RequestNotJSONError
from topchef.models.errors import DeserializationError
from topchef.serializers import JSONSchema
from topchef.serializers import ServiceDetail as ServiceSerializer
from topchef.serializers import ServiceModification as ModifyServiceSerializer


class ServiceDetail(AbstractEndpointForService):
    """
    Describes the endpoint that returns the details for a particular service
    """
    def get(self, service: Service) -> Response:
        r"""
        Return details for a given service

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "description": "A quick testing service",
                    "has_timed_out": true,
                    "id": "495d76fd-044c-4f02-8815-5ec6e7634330",
                    "is_service_available": false,
                    "job_registration_schema": {
                        "type": "object"
                    },
                    "job_result_schema": {
                        "type": "object"
                    },
                    "jobs": [
                        {
                        "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                        "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                        "status": "REGISTERED"
                        }
                    ],
                    "name": "Testing Service",
                    "timeout": 30
                    },
                    "links": {
                        "self":
                            "/services/495d76fd-044c-4f02-8815-5ec6e7634330"
                    },
                    "meta": {
                        "service_schema": {
                            "$schema":
                                "http://json-schema.org/draft-04/schema#",
                            "description":
                                "A comprehensive schema for services",
                            "properties": {
                                "description": {
                                    "readonly": true,
                                    "title": "description",
                                    "type": "string"
                                },
                                "has_timed_out": {
                                    "readonly": true,
                                    "title": "has_timed_out",
                                    "type": "boolean"
                                },
                                "id": {
                                    "format": "uuid",
                                    "readonly": true,
                                    "title": "id",
                                    "type": "string"
                                },
                                "is_service_available": {
                                    "readonly": true,
                                    "title": "is_service_available",
                                    "type": "boolean"
                                },
                                "job_registration_schema": {
                                    "readonly": true,
                                    "title": "job_registration_schema",
                                    "type": "object"
                                },
                                "job_result_schema": {
                                    "readonly": true,
                                    "title": "job_result_schema",
                                    "type": "object"
                                },
                                "jobs": {
                                    "items": {
                                    "type": "object"
                                    },
                                    "type": "array"
                                },
                                "name": {
                                    "readonly": true,
                                    "title": "name",
                                    "type": "string"
                                },
                                "timeout": {
                                    "readonly": true,
                                    "title": "timeout",
                                    "type": "string"
                                }
                            },
                            "required": [
                                "description",
                                "has_timed_out",
                                "id",
                                "is_service_available",
                                "job_registration_schema",
                                "job_result_schema",
                                "name",
                                "timeout"
                            ],
                            "title": "Detailed Service Schema",
                            "type": "object"
                        }
                    }
                }

        :statuscode 200: The request completed successfully
        :statuscode 404: A service with the ID was not found

        :param service: The service for which a response is to be retrieved
        :return: A flask response with the appropriate data
        """
        return self._get_detailed_response_for_service(service)

    def patch(self, service: Service) -> Response:
        """
        Change the mutable parameters of the service

        **Example Request**

        .. sourcecode:: http

            PATCH /services/<service_id> HTTP/1.1
            Content-Type: application/json

            {
                "is_available": false,
                "name": "Changed name",
                "description": "Changed description",
                "timeout": 20
            }

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "description": "A quick testing service",
                "has_timed_out": true,
                "id": "495d76fd-044c-4f02-8815-5ec6e7634330",
                "is_service_available": false,
                "job_registration_schema": {
                    "type": "object"
                },
                "job_result_schema": {
                    "type": "object"
                },
                "jobs": [
                    {
                        "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                        "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                        "status": "REGISTERED"
                    }
                ],
                "name": "Testing Service",
                "timeout": 30
            }

        :statuscode 200: The request completed successfully
        :statuscode 400: If an attempt is made to provide JSON as a request
            body, and the JSON is either syntactically or semantically
            incorrect.
        :statuscode 404: A service with that ID was not found in the database

        :param service: The service to patch
        :return: Reset the service's timeout
        """
        service.check_in()

        try:
            request_body = self.request_json
        except RequestNotJSONError:
            return self._handle_request_not_json()
        else:
            return self._handle_service_modification(request_body, service)

    @staticmethod
    def _handle_request_not_json() -> Response:
        response = jsonify({
            'meta':
                "Service checked in at %s" % datetime.utcnow().isoformat()
        })
        response.status_code = 200
        return response

    def _handle_service_modification(
            self, request_body: dict, service: Service
    ) -> Response:
        serializer = ModifyServiceSerializer()
        deserialized_body, errors = serializer.load(request_body)

        if errors:
            self._report_deserialization_errors(errors)
            raise self.Abort()

        self._modify_service(deserialized_body, service)

        return self._get_detailed_response_for_service(service)

    def _report_deserialization_errors(self, errors: dict):
        self.errors.extend(
            (DeserializationError(key, errors[key]) for key in errors.keys())
        )

    def _get_detailed_response_for_service(self, service: Service) -> Response:
        serializer = ServiceSerializer()
        serializer_schema = JSONSchema(
            title='Detailed Service Schema',
            description='A comprehensive schema for displaying services'
        )
        response = jsonify({
            'data': serializer.dump(service, many=False).data,
            'meta': {'service_schema': serializer_schema.dump(serializer)},
            'links': {'self': self.self_url(service)}
        })
        response.status_code = 200
        return response

    @staticmethod
    def _modify_service(request_body: dict, service: Service) -> None:
        request_body_keys = request_body.keys()
        if 'is_available' in request_body_keys:
            service.is_service_available = request_body['is_available']
        if 'description' in request_body_keys:
            service.description = request_body['description']
        if 'name' in request_body_keys:
            service.name = request_body['name']
        if 'timeout' in request_body_keys:
            service.timeout = request_body['timeout']


class ServiceDetailForServiceID(
    ServiceDetail, metaclass=AbstractEndpointForServiceMeta
):
    """
    Contains a mixin to help the web endpoints parse ``service_id`` string
    as they come raw from the HTTP endpoint
    """

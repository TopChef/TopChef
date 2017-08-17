"""
Describes the endpoint for listing services
"""
from flask import jsonify, Response, request, Request
from sqlalchemy.orm import Session
from typing import Optional
from topchef.api.abstract_endpoints.abstract_endpoint import AbstractEndpoint
from topchef.models import ServiceList as ServiceListInterface
from topchef.models.errors import DeserializationError, SerializationError
from topchef.models.service_list import ServiceList as ServiceListModel
from topchef.serializers import JSONSchema
from topchef.serializers import NewService as NewServiceSerializer
from topchef.serializers import ServiceOverview as ServiceOverviewSerializer


class ServicesList(AbstractEndpoint):
    """
    Maps methods for listing services as well as creating a service
    """
    def __init__(
            self, session: Session,
            flask_request: Request=request,
            service_list: Optional[ServiceListInterface]=None
    ) -> None:
        """

        Create a service list model that is capable of getting services from
        the DB

        :param session: The database session to use
        """
        super(self.__class__, self).__init__(session, flask_request)

        if service_list is not None:
            self.service_list = service_list
        else:
            self.service_list = ServiceListModel(session)

    def get(self) -> Response:
        """
        Returns a list of all services exposed by this API

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                    "description": "A quick testing service",
                    "id": "495d76fd-044c-4f02-8815-5ec6e7634330",
                    "name": "Testing Service"
                    },
                ],
                "links": {
                    "self": "http://localhost:5000/services"
                },
                "meta": {
                    "new_service_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "properties": {
                            "description": {
                                "title": "description",
                                "type": "string"
                            },
                            "job_registration_schema": {
                                "title": "job_registration_schema",
                                "type": "object"
                            },
                            "job_result_schema": {
                                "title": "job_result_schema",
                                "type": "object"
                            },
                            "name": {
                                "title": "name",
                                "type": "string"
                            }
                        },
                        "required": [
                            "description",
                            "job_registration_schema",
                            "job_result_schema",
                            "name"
                        ],
                        "title": "New Service Schema",
                        "type": "object"
                       },
                    "service_schema": {
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "properties": {
                        "description": {
                            "readonly": true,
                            "title": "description",
                            "type": "string"
                        },
                        "id": {
                            "format": "uuid",
                            "readonly": true,
                            "title": "id",
                            "type": "string"
                        },
                        "name": {
                            "readonly": true,
                            "title": "name",
                            "type": "string"
                        }
                    },
                    "required": [
                        "description",
                        "id",
                        "name"
                    ],
                    "title": "Service overview schema",
                    "type": "object"
                    }
                }
            }

        :statuscode 200: The request completed successfully
        :return: A Flask response with the appropriate data
        """
        response = jsonify({
            'data': self._data, 'meta': self._meta, 'links':
            self.links
        })
        response.status_code = 200
        return response

    def post(self) -> Response:
        """
        Create a new service

        **Example Request**

        The request below will create a service for running Rabi experiments
        remotely. The only experiment parameter in this case is the
        ``pulse_time``. In the case of the Rabi experiment, this can
        represent how long the pulse is to be switched on for. Using JSON
        schema, we can also bound the pulse time to be between 0 and 50
        microseconds. This is done because we know ahead of time that it
        would be silly to run Rabi experiments with a negative pulse time.
        All the ``title`` and ``description`` fields in the schema are
        optional, and are there so that humans understand the schema.

        .. warning::

            By default, properties in JSON schema are not required. There
            needs to be a ``required`` keyword with the required parameters
            in the schema in order to mandate that objects have the property.

        .. sourcecode:: http

            POST /services HTTP/1.1
            Host: example.com
            Content-Type: application/json

            {
                "name": "NV Experiments",
                "description": "Describes a sample NV center experiment",
                "job_registration_schema": {
                    "type": "object",
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "Job Registration Schema",
                    "description":
                        "Describes a schema for a Rabi experiment only",
                    "properties": {
                        "pulse_time": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 50e-6
                        }
                    },
                    "required": [
                        "pulse_time"
                    ]
                },
                "job_result_schema": {
                    "type": "object",
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "Job Result Schema",
                    "description": "Describes a schema for the results",
                    "properties": {
                        "light_count": {
                            "type": "integer",
                            "minimum": 0
                        },
                        "dark_count": {
                            "type": "integer",
                            "minimum": 0
                        },
                        "result_count": {
                            "type": "integer",
                            "minimum": 0
                        }
                    },
                    "required": [
                        "light_count",
                        "dark_count",
                        "result_count"
                    ]
                }
            }

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 201 CREATED
            Content-Type: application/json

            {
                "data": {
                    "message": "service successfully created"
                },
                "links": {
                    "self": "http://localhost:5000/services"
                }
            }

        :statuscode 201: The service was successfully created
        :statuscode 400: The request could not be understood, due to either
            incorrect JSON, or not adhering to the schema in the
            ``new_service_schema`` presented in the ``GET`` method of this
            endpoint

        :return: A flask response indicating whether creation of the service
            was successful or not
        """
        serializer = NewServiceSerializer(strict=False, many=False)
        data, errors = serializer.load(self.request_json)

        if errors:
            self._report_client_serialization_errors(errors)
            raise self.Abort()
        else:
            response = self._make_service_from_data(data)

        return response

    @property
    def _data(self) -> dict:
        """

        :return: The JSON corresponding to all the services loaded onto the
            API
        """
        serializer = ServiceOverviewSerializer()
        service_list, errors = serializer.dump(self.service_list, many=True)

        if errors:
            self._report_server_serialization_errors(errors)
            raise self.Abort()

        return service_list

    @property
    def _meta(self) -> dict:
        """

        :return: The endpoint metadata
        """
        service_schema = JSONSchema(
            title='Service overview schema',
            description='The schema for each entry in the services list'
        )
        new_service_schema = JSONSchema(
            title='New Service Schema',
            description='The schema that must be satisfied in order to post '
                        'a new service'
        )
        return {
            'service_schema': service_schema.dump(ServiceOverviewSerializer()),
            'new_service_schema': new_service_schema.dump(
                NewServiceSerializer()
            )
        }

    def _report_client_serialization_errors(self, errors: dict) -> None:
        self.errors.extend(
            DeserializationError(
                source, errors[source]
            ) for source in errors.keys()
        )

    def _report_server_serialization_errors(self, errors: list) -> None:
        self.errors.extend(SerializationError(error) for error in errors)

    def _make_service_from_data(self, data: dict) -> Response:
        self.service_list.new(
            data['name'],
            data['description'],
            data['job_registration_schema'],
            data['job_result_schema']
        )
        return self._make_correct_response()

    def _make_correct_response(self) -> Response:
        response = jsonify({
            'data': {'message': 'service successfully created'},
            'links': self.links
        })
        response.status_code = 201
        return response

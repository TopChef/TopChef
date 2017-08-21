"""
Maps the ``/services/<service_id>/jobs`` endpoint
"""
from flask import Response, jsonify, url_for, Request, request
from topchef.api.abstract_endpoints import AbstractEndpointForService
from topchef.api.abstract_endpoints import AbstractEndpointForServiceMeta
from topchef.api.job_detail import JobDetailForJobID as JobDetail
from topchef.models import Service, ServiceList
from topchef.models.errors import DeserializationError, ValidationError
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobDetailSerializer
from topchef.serializers.new_job import NewJob as NewJobSerializer
from jsonschema import Draft4Validator as JSONSchemaValidator
from typing import Iterable, Optional
from jsonschema import ValidationError as JSONSchemaError
from sqlalchemy.orm import Session


class JobsForServiceEndpoint(AbstractEndpointForService):
    """
    Describes the endpoint. A ``GET`` request to this endpoint returns all
    the jobs registered for a particular service. A ``POST`` request to this
    endpoint will allow the user to create new jobs for the service. A
    ``PATCH`` request here will reset the time since the service was last
    polled
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            service_list: Optional[ServiceList]=None,
            validator_factory: Optional[type]=None
    ):
        super(JobsForServiceEndpoint, self).__init__(
            session, flask_request, service_list=service_list
        )
        if validator_factory is None:
            self._validator_factory = JSONSchemaValidator
        else:
            self._validator_factory = validator_factory

    def get(self, service: Service) -> Response:
        """
        Get the list of jobs available for a service

        .. :quickref: Service; Get jobs for the service

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                        "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                        "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                        "parameters": {
                            "foo": "bar"
                        },
                        "results": {
                            "foo": "bar"
                        },
                        "status": "REGISTERED"
                    }
                ],
                "links": {
                    "self": "http://localhost:5000/services/495d76fd-044c-4f02-8815-5ec6e7634330/jobs"
                },
                "meta": {
                    "data_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The schema for reading data contained in the data key of this response",
                        "items": {
                            "$schema": "http://json-schema.org/draft-04/schema#",
                            "description": "The schema for reading data contained in the data key of this response",
                            "properties": {
                                "date_submitted": {
                                    "format": "date-time",
                                    "title": "date_submitted",
                                    "type": "string"
                                },
                                "id": {
                                    "format": "uuid",
                                    "title": "id",
                                    "type": "string"
                                },
                                "parameters": {
                                    "title": "parameters",
                                    "type": "object"
                                },
                                "results": {
                                    "title": "results",
                                    "type": "object"
                                },
                                "status": {
                                    "enum": [
                                        "REGISTERED",
                                        "WORKING",
                                        "COMPLETED",
                                        "ERROR"
                                    ],
                                    "type": "string"
                                }
                            },
                            "required": [
                                "id",
                                "parameters",
                                "results",
                                "status"
                            ],
                            "title": "Data Schema",
                            "type": "object"
                        },
                        "title": "Data Schema",
                        "type": "array"
                    },
                    "new_job_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The schema that a POST request must satisfy in order to create a new job",
                        "properties": {
                            "parameters": {
                                "type": "object"
                            }
                        },
                        "title": "New Job Schema",
                        "type": "object"
                    }
                }
            }

        :statuscode 200: The request completed successfully
        :statuscode 404: A service with that ID could not be found

        :param service: The service for which jobs are to be retrieved
        :return: A flask response containing the data to display to the user
        """
        serializer = JobDetailSerializer()
        response = jsonify({
            'data': serializer.dump(service.jobs, many=True).data,
            'meta': {
                'new_job_schema': self._new_job_schema(service),
                'data_schema': self._data_schema
            },
            'links': {'self': self.self_url(service)}
        })
        response.status_code = 200
        return response

    def post(self, service: Service) -> Response:
        """
        Create a new job. The request must satisfy the schema specified in the
        key ``meta/new_job_schema``. A request indicating a successful
        response will also include a ``Location`` header indicating where
        the new job is located.

        .. :quickref: Service; create a new job

        **Example Request**

        .. sourcecode:: http

            POST /services/668ac2ea-063d-4122-ba7a-97a3e8e46a8a/jobs HTTP/1.1
            Content-Type: application/json

            {
                "parameters": {
                    "experiment_type": "RABI",
                    "wait_time": 500e-9
                }
            }

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 201 CREATED
            Content-Type: application/json
            Location: http://localhost:5000/jobs/42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7

            {
                "data": {
                    "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                    "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                    "parameters": {
                      "experiment_type": "RABI",
                      "wait_time": 500e-9,
                    },
                    "results": null,
                    "status": "REGISTERED"
                }
                "meta": "new job ID is b0b58425-165f-4add-97b0-86da6b38757f"
            }

        :statuscode 201: The job was successfully created
        :statuscode 400: The job could not be created.
        :statuscode 404: A service with the ID could not be found

        :param service: The service for which the new job is to be made
        :return: A flask response with the appropriate response as per the
            documentation in this endpoint
        """
        data, errors = NewJobSerializer().load(self.request_json)
        if errors:
            self.errors.extend(
                DeserializationError(key, errors[key]) for key in errors.keys()
            )
            raise self.Abort()

        validator = self._validator_factory(service.job_registration_schema)

        if not validator.is_valid(data['parameters']):
            self._report_json_schema_errors(
                validator.iter_errors(data['parameters'])
            )
            raise self.Abort()

        new_job = service.new_job(data['parameters'])

        job_data_serializer = JobDetailSerializer()

        response = jsonify({
            'data': job_data_serializer.dump(new_job).data,
            'meta': 'new job ID is %s' % new_job.id
        })
        response.status_code = 201
        response.headers['Location'] = url_for(
            JobDetail.__name__, job_id=new_job.id, _external=True
        )
        return response

    @staticmethod
    def _new_job_schema(service: Service) -> dict:
        json_schema = JSONSchema(
            title='New Job Schema',
            description='The schema that a POST request must satisfy in '
                        'order to create a new job')
        schema = {
            'title': json_schema.title,
            'description': json_schema.description,
            '$schema': json_schema.schema,
            'type': 'object',
            'properties': {
                'parameters': service.job_registration_schema
            }
        }
        return schema

    @property
    def _data_schema(self) -> dict:
        json_schema = JSONSchema(
            title='Data Schema',
            description='The schema for reading data contained in the data '
                        'key of this response'
        )

        schema = {
            '$schema': json_schema.schema,
            'title': json_schema.title,
            'description': json_schema.description,
            'type': 'array',
            'items': json_schema.dump(JobDetailSerializer())
        }
        return schema

    def _report_json_schema_errors(
            self, errors: Iterable[JSONSchemaError]
    ) -> None:
        self.errors.extend(ValidationError(error) for error in errors)


class JobsForServiceID(
    JobsForServiceEndpoint, metaclass=AbstractEndpointForServiceMeta
):
    """
    Endpoint that maps the web endpoints defined in the superclass to match
    service ids
    """

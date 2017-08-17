"""
Maps the ``jobs/<job_id>`` endpoint
"""
from jsonschema import Draft4Validator as JsonschemaValidator
from jsonschema import ValidationError as JsonSchemaValidatorError
from sqlalchemy.orm import Session
from flask import Response, jsonify, url_for, Request, request
from topchef.models import Job, JobList
from topchef.models.errors import ValidationError
from topchef.api.abstract_endpoints import AbstractEndpointForJob
from topchef.api.abstract_endpoints import AbstractEndpointForJobMeta
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobSerializer
from topchef.serializers import JobModification as JobModificationSerializer
from topchef.models.errors import DeserializationError
from typing import Dict, Optional, Type, Iterable
from uuid import UUID


class JobDetail(AbstractEndpointForJob):
    """
    Contains details for a particular job
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            job_list:Optional[JobList]=None,
            validator_factory: Type[JsonschemaValidator]=JsonschemaValidator
    ) -> None:
        super(JobDetail, self).__init__(
            session, flask_request, job_list
        )
        self._validator_factory = validator_factory

    def get(self, job: Job) -> Response:
        """
        Return the details for a job with a particular ID

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": {
                    "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                    "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                    "parameters": {
                    "foo": "bar"
                    },
                    "results": null,
                    "status": "REGISTERED"
                },
                "links": {
                    "self": "http://localhost:5000/jobs/42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7"
                },
                "meta": {
                    "job_info_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The schema for all displayable data for a job",
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
                        "title": "Detailed Job Schema",
                        "type": "object"
                    },
                    "patch_request_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The schema for all displayable data for a job",
                        "properties": {
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
                        "required": [],
                        "title": "Detailed Job Schema",
                        "type": "object"
                    }
                }
            }

        :statuscode 200: The request completed successfully
        :statuscode 404: A job with that ID could not be found

        :param job: The job for which a response is to be obtained
        :return: A Flask response containing the data for a given job
        """
        serializer = JobSerializer()
        serializer_schema = JSONSchema(
            title='Detailed Job Schema',
            description='The schema for all displayable data for a job'
        )
        job_modification_serializer = JobModificationSerializer()
        response = jsonify({
            'data': serializer.dump(job, many=False).data,
            'meta': {
                'job_info_schema': serializer_schema.dump(serializer),
                'patch_request_schema': serializer_schema.dump(
                    job_modification_serializer
                )
            },
            'links': {
                'self': self._self_url(job.id)
            }
        })
        response.status_code = 200
        return response

    def patch(self, job: Job) -> Response:
        """
        Modify the mutable properties of the job. These are the job status
        and the job results. A request to this endpoint must satisfy the
        schema in the ``patch_request_schema`` key in the ``meta`` key of
        the GET request of this endpoint

        **Example Request**

        Let's say we completed the NV-experiment, and received a light count
        of 153 photons, a dark count of 100 photons, and a result count of
        113 photons. This request will set the job status to "COMPLETED" to
        indicate that the job is finished, and it will update the job
        results. Keep in mind that we need to satisfy the
        ``job_result_schema`` of the job's service in order to post valid
        results. Our results will be validated here.

        .. sourcecode:: http

            PATCH /jobs/42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7 HTTP/1.1
            Content-Type: application/json

            {
                "status": "COMPLETED",
                "results": {
                    "light_count": 153,
                    "dark_count": 100,
                    "result_count": 113
                }
            }

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                "parameters": {
                    "pulse_time": 250e-9
                },
                "results": {
                    "light_count": 153,
                    "dark_count": 100,
                    "result_count": 113
                },
                "status": "COMPLETED"
            }

        :statuscode 200: The request completed successfully
        :statuscode 404: A job with that ID could not be found

        :param job: The job to be modified
        :return: The response
        """
        serializer = JobModificationSerializer()
        job_reporting_serializer = JobSerializer()

        data, errors = serializer.load(self.request_json)

        if errors:
            self._report_loading_errors(errors)
            raise self.Abort()

        if 'results' in data.keys():
            self._modify_job_results(job, data['results'])

        if 'status' in data.keys():
            self._modify_job_status(job, data['status'])

        response = jsonify(job_reporting_serializer.dump(job).data)
        response.status_code = 200
        return response

    def _report_loading_errors(self, errors: Dict[str, str]) -> None:
        self.errors.extend(
            DeserializationError(key, errors[key]) for key in errors.keys()
        )

    def _report_validation_errors(
            self, errors: Iterable[JsonSchemaValidatorError]
    ) -> None:
        self.errors.extend(
            ValidationError(error) for error in errors
        )

    def _self_url(self, job_id: UUID) -> str:
        """

        :param job_id: The ID of the job for which the endpoint has been found
        :return: The URL for the endpoint that was accessed by the user
        """
        return url_for(self.__class__.__name__, job_id=str(job_id),
                       _external=True)

    def _modify_job_results(self, job: Job, results: dict) -> None:
        json_schema_validator = self._validator_factory(job.result_schema)

        if not json_schema_validator.is_valid(results):
            self._report_validation_errors(
                json_schema_validator.iter_errors(results)
            )
            raise self.Abort()
        else:
            job.results = results

    @staticmethod
    def _modify_job_status(job: Job, status: Job.JobStatus) -> None:
        job.status = status


class JobDetailForJobID(
    JobDetail, metaclass=AbstractEndpointForJobMeta
):
    """
    Contains a mixin to map a job UUID to a job endpoint
    """

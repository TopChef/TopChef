"""
Maps the ``services/<service_id>/jobs/next`` endpoint
"""
from datetime import datetime
from .abstract_endpoints import AbstractEndpointForService
from .abstract_endpoints import AbstractEndpointForServiceMeta
from topchef.models import Job, Service
from typing import Optional
from flask import Response, jsonify
from itertools import islice
from topchef.serializers import JobDetail as JobSerializer
from topchef.serializers import JSONSchema


class NextJob(AbstractEndpointForService):
    def get(self, service: Service) -> Response:
        """

        **Example Response With Job**

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
                    "results": {
                        "foo": "bar"
                    },
                    "status": "REGISTERED"
                },
                "links": {
                    "self": "http://localhost:5000/services/495d76fd-044c-4f02-8815-5ec6e7634330/jobs/next"
                },
                "meta": {
                    "job_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The schema representing the job",
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
                        "title": "Job Schema",
                        "type": "object"
                    }
                }
            }

        :statuscode 200: The request completed successfully. The next job is
            available in the request body
        :statuscode 204: The request completed successfully, but no next job
            is available
        :statuscode 404: A service with that ID could not be found

        :param service: The service for which the next job is to be obtained
        :return: A flask response with the appropriate data
        """
        try:
            response = self._get_response_for_job(
                self._get_next_job(service),
                service
            )
        except StopIteration:
            response = self._response_for_no_job

        return response

    @staticmethod
    def _is_registered(job: Job) -> bool:
        return job.status is Job.JobStatus.REGISTERED

    @staticmethod
    def _get_next_job(service: Service) -> Optional[Job]:
        registered_jobs = filter(
            NextJob._is_registered, service.jobs
        )
        return next(
            iter(
                islice(
                    sorted(registered_jobs, key=NextJob._get_date_for_job),
                    1
                )
            )
        )

    @staticmethod
    def _get_date_for_job(job: Job) -> datetime:
        return job.date_submitted

    def _get_response_for_job(
            self, next_job: Job, service: Service
    ) -> Response:
        serializer = JobSerializer()
        schema_serializer = JSONSchema(
            title="Job Schema",
            description="The schema representing the job"
        )
        response = jsonify({
            'data': serializer.dump(next_job).data,
            'meta': {
                'job_schema': schema_serializer.dump(serializer)
            },
            'links': {
                'self': self.self_url(service)
            }
        })
        response.status_code = 200
        return response

    @property
    def _response_for_no_job(self) -> Response:
        response = Response()
        response.status_code = 204
        return response


class NextJobForServiceID(NextJob, metaclass=AbstractEndpointForServiceMeta):
    """
    Maps the service for which jobs are to be obtained into a job ID
    """
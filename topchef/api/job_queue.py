"""
Maps the ``/services/<service_id>/queue`` endpoint
"""
from datetime import datetime
from flask import Response, jsonify
from topchef.api.abstract_endpoints import AbstractEndpointForService
from topchef.api.abstract_endpoints import AbstractEndpointForServiceMeta
from topchef.models import Service, Job
from topchef.serializers import JobDetail, JSONSchema
from itertools import islice
from typing import Iterable


class JobQueueForService(AbstractEndpointForService):
    """
    Maps the endpoint
    """
    def get(self, service: Service) -> Response:
        r"""
        Returns the next 10 jobs available for a given service

        .. :quickref: Job; Get the next few jobs

        **Example Request**

        .. sourcecode:: http

            GET /services/495d76fd-044c-4f02-8815-5ec6e7634330/queue HTTP/1.1
            Content-Type: application/json

        **Example Response With A Job**

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
                        "results": null,
                        "status": "REGISTERED"
                    }
                ],
                "links": {
                    "self": "http://localhost:5000/services/495d76fd-044c-4f02-8815-5ec6e7634330/queue"
                },
                "meta": {
                    "data_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "The schema for the data in the \"data\" key",
                        "items": {
                            "$schema": "http://json-schema.org/draft-04/schema#",
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
                        "type": "object"
                        },
                        "title": "Job List Schema",
                        "type": "array"
                    }
                }
            }

        **Example Response With No Job**

        .. sourcecode:: http

            HTTP/1.1 204 NO CONTENT

        :statuscode 200: The request completed successfully
        :statuscode 204: The request completed successfully, but there are
            no jobs in the queue right now.
        :statuscode 404: A service with that ID could not be found

        :param service: The service for which the next few jobs are to be
            retrieved
        :return: A flask response with the appropriate data
        """
        registered_jobs = filter(
            self._is_job_registered, service.jobs
        )
        first_few_jobs = islice(registered_jobs, 10)
        sorted_jobs_by_date = sorted(
            first_few_jobs,
            key=self._get_date_submitted,
            reverse=False
        )

        if not sorted_jobs_by_date:
            response = Response()
            response.status_code = 204
        else:
            response = jsonify({
                'data': self._get_data(sorted_jobs_by_date),
                'meta': {
                    'data_schema': self.data_schema
                },
                'links': {'self': self.self_url(service)}
            })
            response.status_code = 200

        return response

    @staticmethod
    def _is_job_registered(job: Job):
        """

        :param job: The job to check if it is registered
        :return:
        """
        return job.status is Job.JobStatus.REGISTERED

    @staticmethod
    def _get_date_submitted(job: Job) -> datetime:
        return job.date_submitted

    @staticmethod
    def _get_data(sorted_jobs_by_date: Iterable[Job]) -> dict:
        serializer = JobDetail()
        return serializer.dump(sorted_jobs_by_date, many=True).data

    @property
    def data_schema(self) -> dict:
        entry_schema = JSONSchema()
        return {
            '$schema': entry_schema.schema,
            'title': 'Job List Schema',
            'description': 'The schema for the data in the "data" key',
            'type': 'array',
            'items': entry_schema.dump(JobDetail())
        }


class JobQueueForServiceID(
    JobQueueForService, metaclass=AbstractEndpointForServiceMeta
):
    """
    Modifies the web methods in order to accept and resolve services for a
    given service UUID
    """
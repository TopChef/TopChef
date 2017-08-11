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
                'links': self.links
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
        return serializer.dump(sorted_jobs_by_date, many=True)

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
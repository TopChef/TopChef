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
        try:
            response = self._get_response_for_job(self._get_next_job(service))
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

    def _get_response_for_job(self, next_job: Job) -> Response:
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
            'links': self.links
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
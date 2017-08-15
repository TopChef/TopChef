"""
Maps the ``jobs/<job_id>`` endpoint
"""
from flask import Response, jsonify
from topchef.models import Job
from topchef.api.abstract_endpoints import AbstractEndpointForJob
from topchef.api.abstract_endpoints import AbstractEndpointForJobMeta
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobSerializer
from topchef.serializers import JobModification as JobModificationSerializer
from topchef.models.errors import DeserializationError
from typing import Dict


class JobDetail(AbstractEndpointForJob):
    """
    Contains details for a particular job
    """
    def get(self, job: Job) -> Response:
        """

        :param job: The job for which a response is to be obtained
        :return:
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
            'links': self.links
        })
        response.status_code = 200
        return response

    def patch(self, job: Job) -> Response:
        """

        :param job: The job to be modified
        :return: The response
        """
        serializer = JobModificationSerializer()
        job_reporting_serializer = JobSerializer()

        data, errors = serializer.load(self.request_json)

        if errors:
            self._report_loading_errors(errors)
            raise self.Abort()

        job.status = data['status']
        job.results = data['results']

        response = jsonify(job_reporting_serializer.dump(job).data)
        response.status_code = 200
        return response

    def _report_loading_errors(self, errors: Dict[str, str]) -> None:
        self.errors.extend(
            DeserializationError(key, errors[key]) for key in errors.keys()
        )


class JobDetailForJobID(
    JobDetail, metaclass=AbstractEndpointForJobMeta
):
    """
    Contains a mixin to map a job UUID to a job endpoint
    """

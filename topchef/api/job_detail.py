"""
Maps the ``jobs/<job_id>`` endpoint
"""
from flask import Response, jsonify
from topchef.models import Job
from topchef.api.abstract_endpoints import AbstractEndpointForJob
from topchef.api.abstract_endpoints import AbstractEndpointForJobMeta
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobSerializer


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
        response = jsonify({
            'data': serializer.dump(job, many=False).data,
            'meta': {'job_schema': serializer_schema.dump(serializer)},
            'links': self.links
        })
        response.status_code = 200
        return response


class JobDetailForJobID(
    JobDetail, metaclass=AbstractEndpointForJobMeta
):
    """
    Contains a mixin to map a job UUID to a job endpoint
    """

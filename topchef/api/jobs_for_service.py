"""
Maps the ``/services/<service_id>/jobs`` endpoint
"""
from flask import Response, jsonify
from topchef.api.abstract_endpoints import AbstractEndpointForService
from topchef.api.abstract_endpoints import AbstractEndpointForServiceMeta
from topchef.models import Service
from topchef.models.errors import SerializationError
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobDetailSerializer
from topchef.serializers.new_job import NewJobSchema as NewJobSerializer


class JobsForServiceEndpoint(AbstractEndpointForService):
    """
    Describes the endpoint. A ``GET`` request to this endpoint returns all
    the jobs registered for a particular service. A ``POST`` request to this
    endpoint will allow the user to create new jobs for the service. A
    ``PATCH`` request here will reset the time since the service was last
    polled
    """
    def get(self, service: Service) -> Response:
        serializer = JobDetailSerializer()
        response = jsonify({
            'data': serializer.dump(service.jobs, many=True).data,
            'meta': {
                'new_job_schema': self._new_job_schema(service),
                'data_schema': self._data_schema
            },
            'links': self.links
        })
        response.status_code = 200
        return response

    def post(self, service: Service) -> Response:
        """
        Create a new job

        :param service: The service for which the new job is to be made
        :return:
        """
        data, errors = NewJobSerializer().load(self.request_json)
        if errors:
            self.errors.extend(SerializationError(error) for error in errors)
            raise self.Abort()

        new_job = service.new_job(data['parameters'])

        response = jsonify({'meta': 'new job ID is %s' % new_job.id})
        response.status_code = 201
        return response

    @staticmethod
    def _new_job_schema(service: Service) -> dict:
        return service.job_registration_schema

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


class JobsForServiceID(
    JobsForServiceEndpoint, metaclass=AbstractEndpointForServiceMeta
):
    """
    Endpoint that maps the web endpoints defined in the superclass to match
    service ids
    """

"""
Maps the ``/services/<service_id>/jobs`` endpoint
"""
from typing import Optional
from uuid import UUID

from flask import Request, request, Response, jsonify
from sqlalchemy.orm import Session

from topchef.api.abstract_endpoints.abstract_endpoint import AbstractEndpoint
from topchef.models import ServiceList, Service
from topchef.models.exceptions import NotUUIDError
from topchef.models.exceptions import SerializationError
from topchef.models.exceptions import ServiceWithUUIDNotFound
from topchef.models.service_list import ServiceList as ServiceListModel
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobDetailSerializer
from topchef.serializers.new_job import NewJobSchema as NewJobSerializer


class JobsForServiceEndpoint(AbstractEndpoint):
    """
    Describes the endpoint. A ``GET`` request to this endpoint returns all
    the jobs registered for a particular service. A ``POST`` request to this
    endpoint will allow the user to create new jobs for the service. A
    ``PATCH`` request here will reset the time since the service was last
    polled
    """
    def __init__(
            self, session: Session, flask_request: Request=request,
            service_list: Optional[ServiceList]=None
    ):
        super(JobsForServiceEndpoint, self).__init__(session, flask_request)

        if service_list is None:
            self.service_list = ServiceListModel(session)
        else:
            self.service_list = service_list

    def get(self, service_id: str) -> Response:
        """

        :return: The response containing all the jobs for a given service
        """
        if self._is_uuid(service_id):
            return self._get_response_for_service_id(UUID(service_id))
        else:
            raise NotUUIDError(service_id)

    def post(self, service_id: str) -> Response:
        """

        :param service_id: The ID of the service for which the job is to be
            made
        :return:
        """
        if not self._is_uuid(service_id):
            raise NotUUIDError(service_id)
        else:
            service = self.service_list[UUID(service_id)]

        data, errors = NewJobSerializer().load(self._request.json)
        if errors:
            self.errors.extend(SerializationError(error) for error in errors)
            raise self.Abort()

        new_job = service.new_job(data['parameters'])

        response = jsonify({'meta': 'new job ID is %s' % new_job.id})
        response.status_code = 201
        return response

    def _get_response_for_service_id(self, service_id: UUID):
        try:
            service = self.service_list[service_id]
            return self._get_response_for_service(service)
        except KeyError:
            raise ServiceWithUUIDNotFound(service_id)

    def _get_response_for_service(self, service: Service) -> Response:
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

    def _new_job_schema(self, service: Service) -> dict:
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

    @staticmethod
    def _is_uuid(candidate: str) -> bool:
        try:
            UUID(candidate)
            return True
        except ValueError:
            return False

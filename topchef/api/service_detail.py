"""
Describes an endpoint where detailed information about the service can be
obtained
"""
from flask import Response, jsonify, Request, request
from uuid import UUID
from .abstract_endpoint import AbstractEndpoint
from sqlalchemy.orm import Session
from topchef.models import Service
from topchef.models.service_list import ServiceList as ServiceListModel
from topchef.models.exceptions import ServiceWithUUIDNotFound
from topchef.models.exceptions import NotUUIDError
from topchef.serializers import ServiceDetail as ServiceSerializer
from topchef.serializers import JSONSchema
from typing import Optional


class ServiceDetail(AbstractEndpoint):
    """
    Describes the endpoint that returns the details for a particular service
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            service_list_model: Optional[ServiceListModel]=None
    ) -> None:
        """
        Create the service list model

        :param session: The database session to use for making the request
        """
        super(self.__class__, self).__init__(session, request=flask_request)
        if service_list_model is None:
            self.service_list = ServiceListModel(self.database_session)
        else:
            self.service_list = service_list_model

    def get(self, service_id: str) -> Response:
        """

        :param service_id:
        :return:
        """
        if self._is_uuid(service_id):
            return self._get_response_for_service_uuid(
                UUID(service_id)
            )
        else:
            raise NotUUIDError(service_id)

    def _get_response_for_service_uuid(self, service_id: UUID) -> Response:
        """

        :param service_id: The UUID representing the service ID for which
            data is to be obtained
        :return: The appropriate Flask response stating whether the service
            ID exists or not
        """
        try:
            service = self.service_list[service_id]
        except KeyError:
            raise ServiceWithUUIDNotFound(service_id)
        return self._get_response_for_service(service)

    def _get_response_for_service(self, service: Service) -> Response:
        """

        :param service: The service for which a response is to be retrieved
        :return:
        """
        serializer = ServiceSerializer()
        serializer_schema = JSONSchema(
            title='Detailed Service Schema',
            description='A comprehensive schema for displaying services'
        )
        response = jsonify({
            'data': serializer.dump(service, many=False).data,
            'meta': {'service_schema': serializer_schema.dump(serializer)},
            'links': self.links
        })
        response.status_code = 200
        return response

    @staticmethod
    def _is_uuid(service_id: str):
        """

        :param service_id: The string to check for being a UUID
        :return: ``True`` if it is a UUID and ``False`` if not
        """
        try:
            UUID(service_id)
            return True
        except ValueError:
            return False

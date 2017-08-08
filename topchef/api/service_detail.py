"""
Describes an endpoint where detailed information about the service can be
obtained
"""
from flask import Response
from uuid import UUID
from .abstract_endpoint import AbstractEndpoint
from sqlalchemy.orm import Session
from topchef.models.service_list import ServiceList as ServiceListModel
from typing import Union


class ServiceDetail(AbstractEndpoint):
    """
    Describes the endpoint that returns the details for a particular service
    """
    def __init__(self, session: Session) -> None:
        """
        Create the service list model

        :param session: The database session to use for making the request
        """
        super(self.__class__, self).__init__(session)
        self.service_list = ServiceListModel(self.database_session)

    def get(self, service_id: str) -> Response:
        if self._is_uuid(service_id):
            response = self._get_response_for_service_uuid(
                UUID(service_id)
            )
        else:
            response = self._get_response_for_service_name(service_id)

        return response

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
            response = self._make_response_for_key_error(service_id)
        else:
            response = self._make_response_for_service(service)
        return response

    def _make_response_for_key_error(self, service_id: UUID) -> Response:
        response = jsonify({

        })

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

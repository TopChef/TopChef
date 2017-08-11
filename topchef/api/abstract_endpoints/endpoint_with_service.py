"""
A lot of business logic in the API relies on finding a service for a given
service ID. This abstract endpoint takes care of the endpoints
"""
import abc
from sqlalchemy.orm import Session
from topchef.models import Service, ServiceList
from functools import wraps
from topchef.models.exceptions import ServiceWithUUIDNotFound
from topchef.models.exceptions import NotUUIDError
from topchef.models.service_list import ServiceList as ServiceListModel
from typing import Optional
from uuid import UUID
from topchef.api.abstract_endpoints.abstract_endpoint import AbstractEndpoint
from flask import Response, Request
from flask import request as flask_request


class AbstractEndpointWithService(AbstractEndpoint, metaclass=abc.ABCMeta):
    """
    Describes the endpoint with get methods that retrieve the service
    """
    def __init__(
            self, session: Session, request: Request=flask_request,
            service_list: Optional[ServiceList]=None
    ) -> None:
        super(AbstractEndpointWithService, self).__init__(session, request)

        if service_list is None:
            self._service_list = ServiceListModel(session)
        else:
            self._service_list = service_list

        self._decorate_endpoints()

    def _service_decorator(self, function_to_decorate):
        """

        :param function_to_decorate: The endpoint to decorate
        :return: A decorated function
        """
        @wraps(function_to_decorate)
        def decorated_function(service_id: str, *args, **kwargs) -> Response:
            """

            :param service_id:
            :param args:
            :param kwargs:
            :return:
            """
            if not self._is_uuid(service_id):
                raise NotUUIDError(service_id)

            service = self._get_service(UUID(service_id))

            return function_to_decorate(service, *args, **kwargs)

        return decorated_function

    @staticmethod
    def _is_uuid(service_id: str) -> bool:
        try:
            UUID(service_id)
            return True
        except ValueError:
            return False

    def _get_service(self, service_id: UUID) -> Service:
        try:
            return self._service_list[service_id]
        except KeyError:
            raise ServiceWithUUIDNotFound(service_id)

    def _decorate_endpoints(self) -> None:
        if hasattr(self, 'get'):
            self.get = self._service_decorator(self.get)
        if hasattr(self, 'put'):
            self.put = self._service_decorator(self.put)
        if hasattr(self, 'post'):
            self.post = self._service_decorator(self.post)
        if hasattr(self, 'patch'):
            self.patch = self._service_decorator(self.patch)
        if hasattr(self, 'delete'):
            self.delete = self._service_decorator(self.delete)

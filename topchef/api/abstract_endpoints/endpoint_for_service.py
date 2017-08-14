"""
Takes a more meta approach to wrapping services by providing a metaclass to
use for wrapping the service endpoint
"""
import abc
from functools import wraps
from sqlalchemy.orm import Session
from flask import Response, Request, request
from topchef.models import ServiceList
from topchef.models.service_list import ServiceList as ServiceListModel
from topchef.models.errors import NotUUIDError, ServiceWithUUIDNotFound
from uuid import UUID
from topchef.models import Service
from .abstract_endpoint import AbstractEndpoint, AbstractMethodViewType
from typing import Union, Optional, Iterable


class EndpointForServiceIdMeta(AbstractMethodViewType):
    """
    A metaclass for getting the service
    """
    def __new__(mcs, name, bases, namespace: dict) -> type:
        """

        :param name: The name of the newly-created class
        :param bases: The classes from which this class inherits
        :param namespace: The ``__dict__`` of the instance to be created
        :return:
        """
        if 'methods' not in namespace.keys():
            namespace['methods'] = mcs._get_methods_from_bases(bases)

        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace) -> None:
        super(EndpointForServiceIdMeta, cls).__init__(name, bases, namespace)

        for base in bases:
            if hasattr(base, 'service_list'):
                namespace['service_list'] = base.service_list

        if 'service_list' not in namespace.keys():
            raise ValueError(
                'Unable to create the service wrapper.'
                'The class must have a property called "service_list"'
            )
        else:
            cls.service_list = namespace['service_list']

        cls._decorate_endpoints()

    @staticmethod
    def _get_methods_from_bases(bases: Iterable[type]):
        available_methods = set()
        for base in bases:
            if hasattr(base, 'methods'):
                available_methods.update(method for method in base.methods)
        return list(available_methods)

    def _service_decorator(cls, function_to_decorate):
        """

        :param function_to_decorate: The service endpoint to decorate
        :return:
        """
        @wraps(function_to_decorate)
        def decorated_function(
                instance, service_id: str, *args, **kwargs
        ) -> Response:
            if not cls._is_uuid(service_id):
                raise NotUUIDError(service_id)

            service = cls._get_service(instance, UUID(service_id))

            return function_to_decorate(instance, service, *args, **kwargs)

        return decorated_function

    @staticmethod
    def _is_uuid(service_id: Union[str, UUID]) -> bool:
        if isinstance(service_id, UUID):
            return True
        try:
            UUID(service_id)
            return True
        except ValueError:
            return False

    @staticmethod
    def _get_service(instance, service_id: UUID) -> Service:
        try:
            return instance.service_list[service_id]
        except KeyError:
            raise ServiceWithUUIDNotFound(service_id)

    def _decorate_endpoints(cls) -> None:
        if hasattr(cls, 'get'):
            cls.get = cls._service_decorator(cls.get)
        if hasattr(cls, 'put'):
            cls.put = cls._service_decorator(cls.put)
        if hasattr(cls, 'post'):
            cls.post = cls._service_decorator(cls.post)
        if hasattr(cls, 'patch'):
            cls.patch = cls._service_decorator(cls.patch)
        if hasattr(cls, 'delete'):
            cls.delete = cls._service_decorator(cls.delete)


class AbstractEndpointForServiceMeta(EndpointForServiceIdMeta, abc.ABCMeta):
    """
    Metaclass for endpoints requiring decoration that are also abstract
    classes. This class exists primarily to avoid metaclass conflicts
    """


class AbstractEndpointForService(
    AbstractEndpoint, metaclass=abc.ABCMeta
):
    def __init__(
            self, session: Session, flask_request: Request=request,
            service_list: Optional[ServiceList]=None
    ) -> None:
        super(AbstractEndpointForService, self).__init__(
            session, flask_request
        )
        if service_list is None:
            self._service_list = ServiceListModel(self.database_session)
        else:
            self._service_list = service_list

    @property
    def service_list(self) -> ServiceList:
        return self._service_list

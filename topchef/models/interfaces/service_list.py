"""
Contains an interface for getting services
"""
import abc
from uuid import UUID
from collections.abc import AsyncIterable, MutableMapping
from typing import Union, AsyncIterator, Iterator
from topchef.json_type import JSON_TYPE as JSON
from topchef.models.interfaces.service import Service


class ServiceList(MutableMapping, AsyncIterable, metaclass=abc.ABCMeta):
    """
    Describes an interface for manipulating the set of all services that
    have been posted to the API.
    """
    @abc.abstractmethod
    def __getitem__(self, service_id: UUID) -> Service:
        """

        :param service_id: The ID of the service to retrieve
        :return: The service
        :raises: :exc:`KeyError` if a service with this ID does not exist
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __setitem__(self, service_id: UUID, service: Service) -> None:
        """

        :param service_id:
        :param service:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __delitem__(self, service_id: UUID) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def __contains__(
            self, service_or_service_id: Union[Service, UUID]
    ) -> bool:
        raise NotImplementedError()

    @abc.abstractmethod
    def __aiter__(self) -> AsyncIterator[Service]:
        raise NotImplementedError()

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Service]:
        raise NotImplementedError()

    @abc.abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError()

    @abc.abstractmethod
    def new(
            self, name: str, description: str, registration_schema: JSON,
            result_schema: JSON
    ) -> Service:
        raise NotImplementedError()

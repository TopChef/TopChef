"""
Contains a generator for making service lists
"""
from unittest import mock
from sqlalchemy.orm import Session
from hypothesis.strategies import composite, lists
from tests.unit.model_generators.service import services
from tests.unit.model_generators.service import Service as MockService
from topchef.models import ServiceList as ServiceListInterface
from topchef.models import Service as ServiceInterface
from topchef.json_type import JSON_TYPE as JSON
from typing import Iterable, Union, Iterator
from uuid import UUID


class _ServiceList(ServiceListInterface):
    """
    Contains a mock implementation of the service list interface
    """
    def __init__(self, service_sequence: Iterable[ServiceInterface]) -> None:
        self._services = {
            service.id: service for service in service_sequence
        }

    def __getitem__(self, service_id: UUID) -> ServiceInterface:
        return self._services[service_id]

    def __setitem__(self, service_id: UUID, service: ServiceInterface) -> None:
        self._services[service_id] = service

    def __delitem__(self, service_id: UUID) -> None:
        del self._services[service_id]

    def __contains__(self, item: Union[ServiceInterface, UUID]) -> bool:
        return item in self._services.keys() or item in self._services.values()

    def __aiter__(self):
        raise NotImplementedError()

    def __iter__(self) -> Iterator[ServiceInterface]:
        return iter(self._services.values())

    def __len__(self) -> int:
        return len(self._services.keys())

    def new(
            self, name: str, description: str, registration_schema: JSON,
            result_schema: JSON
    ) -> ServiceInterface:
        return MockService.new(
            name, description, registration_schema, result_schema,
            mock.MagicMock(spec=Session)  # type: Session
        )


@composite
def service_lists(
        draw,
        min_size=None, average_size=None, max_size=None,
        unique_by=None, unique=False
) -> _ServiceList:
    service_generator = lists(
        services(), min_size=min_size, average_size=average_size,
        max_size=max_size, unique_by=unique_by, unique=unique
    )
    return _ServiceList(draw(service_generator))

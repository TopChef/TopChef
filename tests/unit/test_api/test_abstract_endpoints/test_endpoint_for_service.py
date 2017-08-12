"""
Contains unit tests for the endpoint with service wrapper
"""
import unittest
import unittest.mock as mock
from uuid import UUID
from flask import Response, jsonify
from topchef.api.abstract_endpoints import EndpointForServiceIdMeta
from topchef.models import ServiceList, Service
from topchef.models.errors import NotUUIDError, ServiceWithUUIDNotFound
from hypothesis import given, assume, settings
from hypothesis.strategies import text, uuids
from tests.unit.model_generators.service_list import service_lists


class TestEndpointForService(unittest.TestCase):
    """
    Base class for unit testing the metaclass
    """
    class ServiceEndpointSubtype(object, metaclass=EndpointForServiceIdMeta):
        """
        A type that uses the metaclass
        """
        def __init__(self, service_list: ServiceList) -> None:
            self._service_list = service_list
            self._service = None

        @property
        def service_list(self) -> ServiceList:
            return self._service_list

        def get(self, service: Service) -> Response:
            self._service = service
            response = Response(response='{}'.encode('utf-8'))
            response.status_code = 200
            return response

        def put(self, service: Service) -> Response:
            pass

        def post(self, service: Service) -> Response:
            pass

        def patch(self, service: Service) -> Response:
            pass

        def delete(self, service: Service) -> Response:
            pass

    class ServiceEndpointSubTypeChild(ServiceEndpointSubtype):
        """
        Inherit from the parent which contains a ``service_list``
        """
        def __init__(self, service_list: ServiceList):
            super().__init__(service_list)

    class InvalidEndpointSubtype(object):
        """
        A type that does not contain a ``service_list`` for the metaclass to
        use
        """


class TestInit(TestEndpointForService):
    def test_invalid_endpoint(self):
        """

        Tests that creating an invalid endpoint will result in a
        ``ValueError`` being thrown
        """
        with self.assertRaises(ValueError):
            EndpointForServiceIdMeta(
                self.InvalidEndpointSubtype.__name__,
                (object, ),
                {}
            )

    def test_valid_endpoint(self):
        service_list = mock.MagicMock(spec=ServiceList)  # type: ServiceList
        endpoint = self.ServiceEndpointSubtype(service_list)
        self.assertEqual(service_list, endpoint.service_list)

    def test_type_inheriting_from_valid_endpoint(self):
        service_list = mock.MagicMock(spec=ServiceList)  # type: ServiceList
        endpoint = self.ServiceEndpointSubTypeChild(service_list)
        self.assertEqual(service_list, endpoint.service_list)


class TestServiceDecorator(TestEndpointForService):
    """
    Contains tests for the service decorator
    """
    @given(text(), service_lists())
    def test_input_not_uuid(
            self, service_id: str, service_list: ServiceList
    ) -> None:
        """

        :param service_id: The randomly-generated ID to test
        :param service_list: A randomly-generated set of services
        :return:
        """
        assume(not self._is_uuid(service_id))
        endpoint = self.ServiceEndpointSubtype(service_list)

        with self.assertRaises(NotUUIDError):
            endpoint.get(service_id)

    @given(uuids(), service_lists())
    def test_input_service_not_found(
            self, service_id: UUID, service_list: ServiceList
    ) -> None:
        assume(service_id not in (service.id for service in service_list))
        endpoint = self.ServiceEndpointSubtype(service_list)

        with self.assertRaises(ServiceWithUUIDNotFound):
            endpoint.get(str(service_id))

    @given(service_lists())
    @settings(perform_health_check=False)
    def test_get_service(self, service_list: ServiceList):
        assume(len(service_list) > 0)
        service_id = self._first_service_id(service_list)
        endpoint = self.ServiceEndpointSubtype(service_list)
        response = endpoint.get(str(service_id))
        self.assertEqual(response.status_code, 200)

    @staticmethod
    def _is_uuid(service_id: str) -> bool:
        try:
            UUID(service_id)
            return True
        except ValueError:
            return False

    @staticmethod
    def _first_service_id(service_list: ServiceList):
        return next((service.id for service in service_list))

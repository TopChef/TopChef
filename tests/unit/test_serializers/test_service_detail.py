"""
Contains unit tests for the service serializer
"""
import unittest
from hypothesis import given, assume
from topchef.models import Service, Job, ServiceList
from topchef.serializers import ServiceDetail as ServiceSerializer
from tests.unit.model_generators.service import services
from tests.unit.model_generators.service_list import service_lists


class TestServiceDetail(unittest.TestCase):
    """
    Base class for testing the serializer
    """
    def setUp(self) -> None:
        """
        Create a serializer for testing
        """
        self.serializer = ServiceSerializer()


class TestSingleServiceSerialization(TestServiceDetail):
    """
    Contains unit tests for the serializer in order to control serialization
    to a single service
    """
    @given(services())
    def test_serialize_service_without_jobs(self, service: Service) -> None:
        assume(not service.jobs)
        _, errors = self.serializer.dump(service, many=False)
        self.assertFalse(errors)

    @given(services())
    def test_serialize_one_service(self, service: Service) -> None:
        """
        Tests that a serializer successfully serializes to one service

        :param service: The randomly-generated service to serialize
        """
        data, errors = self.serializer.dump(service, many=False)
        self.assertFalse(errors)

    @given(service_lists())
    def test_serialize_many_services(self, service_list: ServiceList) -> None:
        """

        :param service_list: A list of randomly-generated services
        """
        _, errors = self.serializer.dump(service_list, many=True)
        self.assertFalse(errors)

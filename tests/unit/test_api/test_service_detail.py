"""
Contains unit tests for the ``/services/<service_id>`` endpoint
"""
import json
import unittest
import unittest.mock as mock
from topchef.api.service_detail import ServiceDetail
from sqlalchemy.orm import Session
from flask import Flask, Request
from hypothesis import given, settings
from topchef.models import Service, ServiceList
from topchef.serializers import ServiceDetail as ServiceSerializer
from tests.unit.model_generators.service import services


class TestServiceDetail(unittest.TestCase):
    """
    Base class for unit testing the API
    """
    def setUp(self) -> None:
        """
        Set up some mock model classes and create an endpoint
        """
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request
        self.service_list = mock.MagicMock(
            spec=ServiceList
        )  # type: ServiceList

        self._app = Flask(__name__)
        self._app.add_url_rule(
            '/', view_func=ServiceDetail.as_view(
                ServiceDetail.__name__, self.session
            )
        )

        self._context = self._app.test_request_context()

        self._context.push()

    def tearDown(self):
        """

        Pop the test request context
        """
        self._context.pop()


class TestGet(TestServiceDetail):
    """
    Contains unit tests for the ``get`` method
    """
    @given(services())
    @settings(perform_health_check=False)
    def test_get(self, service: Service):
        endpoint = ServiceDetail(
            self.session, self.request, self.service_list
        )
        response = endpoint.get(service)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.data.decode('utf-8'))

        self._assert_data_equal(data['data'], service)

    def _assert_data_equal(self, data: dict, service: Service) -> None:
        serializer = ServiceSerializer()
        self.assertEqual(data, serializer.dump(service).data)

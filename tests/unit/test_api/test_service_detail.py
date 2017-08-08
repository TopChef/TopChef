"""
Contains unit tests for the ``/services/<service_id>`` endpoint
"""
import unittest
import unittest.mock as mock
from uuid import UUID
from topchef.models import ServiceList, Service
from topchef.api import ServiceDetail
from topchef.models.exceptions import NotUUIDError, ServiceWithUUIDNotFound
from sqlalchemy.orm import Session
from flask import Flask
from hypothesis import given
from hypothesis.strategies import text, uuids, dictionaries, booleans


class TestServiceDetail(unittest.TestCase):
    """
    Base class for unit testing the API
    """
    def setUp(self) -> None:
        """
        Set up some mock model classes and create an endpoint
        """
        self.session = mock.MagicMock(spec=Session)
        self.service_list = mock.MagicMock(spec=ServiceList)
        self.service_list_constructor = mock.MagicMock(
            spec=type, return_value=self.service_list
        )

        self.endpoint = ServiceDetail(
            self.session, self.service_list_constructor
        )

        self._app = Flask(__name__)
        self._app.add_url_rule(
            '/', view_func=self.endpoint.__class__.as_view(
                self.endpoint.__class__.__name__, self.session
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
    def setUp(self):
        TestServiceDetail.setUp(self)
        self.service = mock.MagicMock(spec=Service)

    @given(text())
    def test_get_not_uuid(self, bad_id: str) -> None:
        """
        Tests that if a string is passed in, that a ``NotUUIDError`` is raised

        :param bad_id: A string that cannot be converted to a UUID
        """
        with self.assertRaises(NotUUIDError) as assertion:
            self.endpoint.get(bad_id)

        self.assertEqual(
            404, assertion.exception.status_code
        )

    @given(uuids())
    def test_get_service_not_found(self, service_id: UUID) -> None:
        """
        Tests that a ``ServiceWithUUIDNotFound`` is thrown if a service with
        this ID is not found

        :param service_id: The ID for which a service does not exist
        """
        self.service_list.__getitem__ = mock.MagicMock(side_effect=KeyError())
        with self.assertRaises(ServiceWithUUIDNotFound) as assertion:
            self.endpoint.get(str(service_id))

        self.assertEqual(
            404, assertion.exception.status_code
        )

    @given(
        uuids(),
        text(),
        text(),
        dictionaries(text(), text()),
        dictionaries(text(), text()),
        booleans()
    )
    def test_get_service_happy_path(
            self, service_id: UUID, name: str, description: str,
            reg_schema: dict, res_schema: dict, is_available: bool
    ) -> None:
        """

        Tests that a valid service gives a ``200`` response from the detail
        endpoint

        :param service_id: A randomly-generated service ID
        :param name: A random service name
        :param description: A random description
        :param reg_schema: A random job registration schema
        :param res_schema: A random job result schema
        :param is_available: A random flag for service availabilty
        """
        self.service.id = service_id
        self.service.name = name
        self.service.description = description
        self.service.job_registration_schema = reg_schema
        self.service.job_result_schema = res_schema
        self.service.is_available = is_available
        self.service.jobs = []

        self.service_list.__getitem__ = mock.MagicMock(
            return_value=self.service
        )

        response = self.endpoint.get(str(service_id))
        self.assertEqual(200, response.status_code)

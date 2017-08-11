"""
Contains unit tests for
:mod:`topchef.api.abstract_endpoints.endpoint_with_service`
"""
import unittest
import unittest.mock as mock
from topchef.models import Service, ServiceList
from typing import Optional
from flask import Request, Flask
from flask import request as flask_request
from sqlalchemy.orm import Session
from topchef.api.abstract_endpoints.endpoint_with_service import AbstractEndpointWithService
from topchef.models.exceptions import NotUUIDError
from topchef.models.exceptions import ServiceWithUUIDNotFound
from tests.unit.model_generators.service_list import service_lists
from hypothesis import given, assume
from hypothesis.strategies import text, uuids
from uuid import UUID


class TestAbstractEndpointWithService(unittest.TestCase):
    """
    Base class for the unit tests
    """
    def setUp(self) -> None:
        """
        Create a mock concrete endpoint with some methods
        """
        self.session = mock.MagicMock(spec=Session)
        self.request = mock.MagicMock(spec=Request)
        self._app = Flask(__name__)
        self._app.add_url_rule(
            '/',
            view_func=self.ConcreteEndpointWithService.as_view(
                self.ConcreteEndpointWithService.__name__
            )
        )

    class ConcreteEndpointWithService(AbstractEndpointWithService):
        """
        A concrete endpoint to use for testing
        """
        def __init__(
                self,
                session: Session,
                request: Request=flask_request,
                service_list: Optional[ServiceList]=None
        ):
            super(
                TestAbstractEndpointWithService.ConcreteEndpointWithService,
                self
            ).__init__(session, request, service_list)
            self.service = None

        def get(self, service: Service):
            """

            :param service: The service to get
            :return:
            """
            self.service = service

        def patch(self, service: Service):
            self.service = service

        def post(self, service: Service):
            self.service = service

        def put(self, service: Service):
            self.service = service

        def delete(self, service: Service):
            self.service = service


class TestDecoratedEndpointMethod(TestAbstractEndpointWithService):

    @given(service_lists(), text())
    def test_service_id_not_uuid(
            self, service_list: ServiceList,
            bad_service_id: str
    ) -> None:
        assume(not self._is_uuid(bad_service_id))
        endpoint = self.ConcreteEndpointWithService(
            self.session, self.request, service_list=service_list
        )
        with self.assertRaises(NotUUIDError):
            endpoint.get(bad_service_id)

    @staticmethod
    def _is_uuid(candidate_text: str):
        try:
            UUID(candidate_text)
            return True
        except ValueError:
            return False

    @given(service_lists(), uuids())
    def test_service_not_found(
            self,
            service_list: ServiceList,
            service_id: UUID
    ) -> None:
        """

        Tests that if a service is not found, that the abstract endpoint
        correctly handles the error
        """
        assume(service_id not in (service.id for service in service_list))
        endpoint = self.ConcreteEndpointWithService(
            self.session, self.request, service_list=service_list
        )
        with self.assertRaises(ServiceWithUUIDNotFound):
            endpoint.get(str(service_id))

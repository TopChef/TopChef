"""
Contains unit tests for :meth:`topchef.api_server.get_services`
"""
import json
import pytest
from tests.unit.test_api_server import UnitTestWithService


class TestGetServices(UnitTestWithService):
    """
    Contains the unit tests
    """
    @property
    def endpoint(self):
        return '/services'

    def test_get_services(self, _posted_service):
        """
        Tests the method
        """
        response = _posted_service.get(
            self.endpoint, headers=self.headers
        )
        assert response.status_code == self.status_codes['success']

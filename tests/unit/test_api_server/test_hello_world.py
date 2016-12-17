"""
Contains unit tests for :meth:`topchef.api_server.hello_world`
"""
from tests.unit.test_api_server import UnitTest


class TestRootEndpoint(UnitTest):
    """
    Tests the ``/`` endpoint
    """
    @property
    def endpoint(self):
        """
        :return: The endpoint to test
        """
        return '/'

    def test_get_request(self, _app_client):
        response = _app_client.get(self.endpoint, self.headers)

        assert response.status_code == 200

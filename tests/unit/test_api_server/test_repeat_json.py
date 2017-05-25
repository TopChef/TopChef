"""
Contains unit tests for :meth:`topchef.api_server.echo_json`
"""
import json
from tests.unit.test_api_server import UnitTest


class TestLoopback(UnitTest):
    """
    Tests that the JSON repeater at ``/echo`` returns the correct
    responses when JSON is passed into it. For clients that don't have
    native JSON support (I know, right?), they can use this endpoint, pass
    in any string of their choice, and the endpoint will return ``200`` if it
    is valid JSON.
    """
    @property
    def endpoint(self):
        """
        :return: The endpoint to be tested
        """
        return '/echo'

    valid_json = json.dumps({'foo': 'string', 'bar': 1, 'baz': True})
    invalid_json = 'not JSON'

    def test_loopback_valid_json(self, _app_client):
        """
        Tests that the client returns the 200 response
        :param _app_client: The client to be used in making the test.
        """
        response = _app_client.post(
            self.endpoint, headers=self.headers,
            data=self.valid_json
        )

        assert response.status_code == 200

        dict_from_loop = json.loads(response.data.decode('utf-8'))
        dict_from_json = json.loads(self.valid_json)

        assert dict_from_loop['data'] == dict_from_json

    def test_loopback_invalid_json(self, _app_client):
        """
        Tests that the endpoint is capable of processing invalid JSON
        :param _app_client: The client to be used for the test
        """
        response = _app_client.post(
            self.endpoint, headers=self.headers,
            data=self.invalid_json
        )

        assert response.status_code == 400

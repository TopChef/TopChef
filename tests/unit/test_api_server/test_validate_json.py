"""
Contains unit tests for :meth:`topchef.api_server.validate_json`
"""
import json
import jsonschema
from tests.unit.test_api_server import UnitTest


class TestJSONSchemaValidator(UnitTest):
    """
    Contains the unit tests
    """
    @property
    def endpoint(self):
        """
        :return: The endpoint that is to be returned
        """
        return '/validator'

    VALID_JSON = {'value': 1}
    INVALID_JSON = {'value': 'string'}
    SCHEMA = {"type": "object", "properties": {"value": {"type": "integer"}}}

    def test_get_endpoint(self, _app_client):
        response = _app_client.get(
            self.endpoint, headers=self.headers
        )
        assert response.status_code == 200

        schema = json.loads(response.data.decode('utf-8'))['meta'][
            'validation_schema']

        assert jsonschema.validate(
            {'object': self.VALID_JSON, 'schema': self.SCHEMA},
            schema
        ) is None

    def test_validate_200(self, _app_client):
        valid_data = {'object': self.VALID_JSON, 'schema': self.SCHEMA}
        response = _app_client.post(
            self.endpoint, headers=self.headers, data=json.dumps(valid_data)
        )

        assert response.status_code == 200

    def test_validate_400(self, _app_client):
        valid_data = {'object': self.INVALID_JSON, 'schema': self.SCHEMA}

        response = _app_client.post(
            self.endpoint, headers=self.headers, data=json.dumps(valid_data)
        )

        assert response.status_code == 400
        assert json.loads(response.data.decode('utf-8'))['errors']

    def test_validate_invalid_schema(self, _app_client):
        data = {'object': self.VALID_JSON, 'schema': 'string'}

        response = _app_client.post(
            self.endpoint, headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )

        assert response.status_code == 400
        assert json.loads(response.data.decode('utf-8'))['errors']

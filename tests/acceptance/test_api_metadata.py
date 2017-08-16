"""
Contains acceptance tests for ``api_metadata``
"""
import json
import jsonschema
from tests.acceptance import AcceptanceTestCase


class TestAPIMetadata(AcceptanceTestCase):
    """
    Contains an acceptance test for the root endpoint
    """
    @property
    def url(self) -> str:
        """

        :return: The URL of the root endpoint of the API. This will be
            contacted in order to
        """
        return '%s/' % self.app_url

    @property
    def headers(self) -> dict:
        return {'Content-Type': 'application/json'}

    def setUp(self) -> None:
        """
        Set up the endpoint to contact
        """
        AcceptanceTestCase.setUp(self)

    def test_api_metadata(self) -> None:
        """

        Tests that the API metadata returns a correct response, and that the
         data can be validated against the endpoint's schema
        """
        response = self.client.get(self.url, headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data.decode('utf-8'))

        validator = jsonschema.Draft4Validator(
            data['meta']['schema']
        )

        if not validator.is_valid(data['data']):
            self.fail(
                'Errors were encountered while validating response: %s' % (
                    ', '.join(error for error in validator.iter_errors())
                )
            )

"""
Tests that the services can be successfully interrogated after posting a job
"""
from tests.acceptance import AcceptanceTestCaseWithJob


class TestServiceDetail(AcceptanceTestCaseWithJob):
    """
    Tests that the service can be looked at after posting a job
    """
    @property
    def working_service_url(self) -> str:
        """

        :return: A URL to the service detail page that ought to work
        """
        return '%s/services/%s' % (self.app_url, self.service.id)

    @property
    def headers(self) -> dict:
        """

        :return: The headers for making the request
        """
        return {'Content-Type': 'application/json'}

    def test_get_services(self) -> None:
        """
        Tests that the service correctly returns service details if another
        job was posted

        """
        response = self.client.get(
            self.working_service_url, headers=self.headers
        )
        self.assertEqual(response.status_code, 200)

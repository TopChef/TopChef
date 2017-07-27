from tests.integration import IntegrationTestCaseWithService
from topchef.database.models import Service


class TestNew(IntegrationTestCaseWithService):
    """
    Base class for unit testing the new classmethod
    """
    def test_new(self):
        service = Service.new(
            self.service_name, self.service_description,
            self.job_registration_schema, self.job_result_schema
        )
        self.assertNotEqual(service.id, self.service_id)
        self.assertNotEqual(service, self.service)

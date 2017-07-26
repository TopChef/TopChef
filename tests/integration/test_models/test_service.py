from tests.integration import IntegrationTestCaseWithService
from topchef.models import Service


class TestService(IntegrationTestCaseWithService):
    """
    Base class for testing the TopChef service
    """


class TestFromStorage(IntegrationTestCaseWithService):
    """
    Tests the from storage constructor
    """
    def test_from_storage(self):
        service_from_storage = Service.from_storage(
            self.service_id, self.session_factory(),
            self.storage
        )

        self.assertEqual(self.service, service_from_storage)

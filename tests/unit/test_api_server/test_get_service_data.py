"""
Contains unit tests for :meth:`topchef.api_server.get_service_data`
"""
from uuid import uuid4
from . import UnitTestWithService


class TestGetServiceData(UnitTestWithService):

    @property
    def endpoint(self):
        return self._template_endpoint % self.service_id

    @property
    def invalid_endpoint_not_uuid(self):
        return self._template_endpoint % self.bad_service_name

    @property
    def invalid_endpoint_bad_uuid(self):
        bad_uuid = uuid4()
        assert bad_uuid != self.service_id

        return self._template_endpoint % str(bad_uuid)

    def test_get_good_data(self, _posted_service):
        response = _posted_service.get(self.endpoint, headers=self.headers)

        assert response.status_code == self.status_codes['success']

    def test_get_service_not_uuid(self, _posted_service):
        response = _posted_service.get(
            self.invalid_endpoint_not_uuid, headers=self.headers
        )

        assert response.status_code == self.status_codes['not found']

    def test_get_service_uuid_not_found(self, _posted_service):
        response = _posted_service.get(
            self.invalid_endpoint_bad_uuid, headers=self.headers
        )

        assert response.status_code == self.status_codes['not found']

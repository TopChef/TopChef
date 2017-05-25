"""
Contains unit tests for :meth:`topchef.api_server.heartbeat()`
"""
from uuid import uuid4
from . import UnitTestWithService


class TestHeartBeat(UnitTestWithService):
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

    def test_heartbeat_happy_path(self, _posted_service):
        response = _posted_service.patch(self.endpoint)

        assert response.status_code == self.status_codes['success']

    def test_hearbeat_not_uuid(self, _posted_service):
        response = _posted_service.patch(
            self.invalid_endpoint_not_uuid, headers=self.headers
        )

        assert response.status_code == self.status_codes['not found']

    def test_heartbeat_service_not_found(self, _posted_service):
        response = _posted_service.patch(
            self.invalid_endpoint_bad_uuid, headers=self.headers
        )

        assert response.status_code == self.status_codes['not found']

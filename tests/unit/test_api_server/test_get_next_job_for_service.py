from . import UnitTestWithJob
from uuid import uuid4, UUID
import pytest
import json


class TestGetNextJobForService(UnitTestWithJob):
    """
    Get next job for the service
    """

    _invalid_job_id = None
    _invalid_service_id = None
    _second_job_id = None

    @pytest.yield_fixture
    def _second_job(self, _posted_service):
        response = _posted_service.post(
            self._jobs_poster_template % self.service_id,
            headers=self.headers, data=json.dumps(self._valid_job_schema)
        )

        data = json.loads(response.data.decode('utf-8'))
        self._second_job_id = UUID(data['data']['job_details']['id'])

        yield _posted_service

    @property
    def invalid_job_id(self):
        if self._invalid_job_id is None:
            self._invalid_job_id = self._make_new_uuid(self.job_id)
        return self._invalid_job_id

    @property
    def second_job_id(self):
        return self._second_job_id

    @staticmethod
    def _make_new_uuid(uuid_to_avoid):
        new_uuid = uuid4()
        assert new_uuid != uuid_to_avoid
        return new_uuid

    @property
    def invalid_service_id(self):
        if self._invalid_service_id is None:
            self._invalid_service_id = self._make_new_uuid(self.service_id)
        return self._invalid_service_id

    @property
    def endpoint(self):
        return self._jobs_poster_template % self.service_id

    @property
    def invalid_service_endpoint(self):
        return self._jobs_poster_template % self.invalid_service_id

    @property
    def invalid_jobs_endpoint(self):
        return self._jobs_poster_template % self.invalid_service_id

    @property
    def next_job_endpoint(self):
        return '%s/next' % (self._jobs_poster_template % self.service_id)

    def test_happy_path(self, _posted_job, _second_job):
        response = _second_job.get(
            self.next_job_endpoint, headers=self.headers
        )

        data = json.loads(response.data.decode('utf-8'))
        assert response.status_code == 200
        assert self.second_job_id == UUID(data['data']['id'])

    def test_no_job(self, _posted_service):
        response = _posted_service.get(
            self.next_job_endpoint, headers=self.headers
        )
        assert response.status_code == 204

    def test_no_service(self, _posted_service):
        response = _posted_service.get(
            '%s/next' % self.invalid_service_endpoint, headers=self.headers
        )
        assert response.status_code == 404

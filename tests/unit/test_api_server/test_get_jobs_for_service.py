from . import UnitTestWithJob
from uuid import uuid4

class TestGetJobsForService(UnitTestWithJob):

    _invalid_job_id = None
    _invalid_service_id = None

    @property
    def invalid_job_id(self):
        if self._invalid_job_id is None:
            self._invalid_job_id = self._make_new_uuid(self.job_id)
        return self._invalid_job_id

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

    @staticmethod
    def _make_new_uuid(uuid_to_avoid):
        new_uuid = uuid4()
        assert new_uuid != uuid_to_avoid
        return new_uuid

    def test_happy_path(self, _posted_job):
        response = _posted_job.get(self.endpoint, headers=self.headers)

        assert response.status_code == self.status_codes['success']

    def test_service_not_found(self, _posted_job):
        response = _posted_job.get(
            self.invalid_service_endpoint, headers=self.headers
        )

        assert response.status_code == self.status_codes['not found']

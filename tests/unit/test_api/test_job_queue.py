"""
Contains unit tests for the job queue endpoint
"""
import unittest
import unittest.mock as mock
from sqlalchemy.orm import Session
from flask import Request, Flask
from topchef.api.job_queue import JobQueueForService
from topchef.models import Service, ServiceList
from tests.unit.model_generators.service import services
from hypothesis import given, assume, settings
from typing import Sized


class TestJobQueue(unittest.TestCase):
    def setUp(self) -> None:
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request
        self.service_list = mock.MagicMock(
            spec=ServiceList
        )  # type: ServiceList

        _app = Flask(__name__)
        _app.add_url_rule(
            '/', view_func=JobQueueForService.as_view(
                JobQueueForService.__name__
            )
        )
        self._context = _app.test_request_context()
        self._context.push()

    def tearDown(self) -> None:
        self._context.pop()


class TestGet(TestJobQueue):
    @given(services())
    def test_no_jobs_returns_204(self, service: Service) -> None:
        assume(len(service.jobs) == 0)
        endpoint = JobQueueForService(
            self.session, self.request, self.service_list
        )
        response = endpoint.get(service)
        self.assertEqual(204, response.status_code)

    @given(services())
    @settings(perform_health_check=False)
    def test_jobs_registered_returns_200(self, service: Service) -> None:
        assume(len(self._registered_jobs_for_service(service)) > 0)
        endpoint = JobQueueForService(
            self.session, self.request, self.service_list
        )
        response = endpoint.get(service)
        self.assertEqual(200, response.status_code)

    @staticmethod
    def _registered_jobs_for_service(service: Service) -> Sized:
        return set(filter(
            lambda job: job.status is job.JobStatus.REGISTERED, service.jobs
        ))

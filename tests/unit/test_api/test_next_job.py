"""
Contains unit tests for the next job endpoint
"""
import unittest
import unittest.mock as mock
from topchef.api.next_job import NextJob
from hypothesis import given, assume
from topchef.models import Job
from typing import Sequence
from tests.unit.model_generators.service import services
from topchef.models import Service
from sqlalchemy.orm import Session
from flask import Request, Flask


class TestNextJob(unittest.TestCase):
    """
    Base class for unit testing the ``next_job`` endpoint
    """
    def setUp(self) -> None:
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request
        app = Flask(__name__)
        app.add_url_rule('/', view_func=NextJob.as_view(
            NextJob.__name__
        ))
        self.context = app.test_request_context()
        self.context.push()

    def tearDown(self) -> None:
        self.context.pop()


class TestGet(TestNextJob):
    @given(services())
    def test_get_job_available(self, service: Service) -> None:
        assume(len(self._registered_jobs(service)) > 1)
        endpoint = NextJob(self.session, self.request)
        response = endpoint.get(service)
        self.assertEqual(200, response.status_code)

    @given(services())
    def test_get_job_unavailable(self, service: Service) -> None:
        assume(len(self._registered_jobs(service)) == 0)
        endpoint = NextJob(self.session, self.request)
        response = endpoint.get(service)
        self.assertEqual(204, response.status_code)

    @staticmethod
    def _registered_jobs(service: Service) -> Sequence[Job]:
        return tuple(
            job for job in service.jobs
            if job.status == Job.JobStatus.REGISTERED
        )

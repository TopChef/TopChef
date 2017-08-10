"""
Contains unit tests for the ``/jobs`` endpoint
"""
import unittest
import json
import unittest.mock as mock
from flask import Request, Flask
from sqlalchemy.orm import Session
from topchef.api import JobsList
from topchef.models import JobList as JobListInterface
from topchef.serializers import JobOverview
from hypothesis import given
from tests.unit.model_generators import job_lists


class TestJobList(unittest.TestCase):
    """
    Base class for unit testing the ``/jobs`` endpoint
    """
    def setUp(self) -> None:
        """
        Create a mock Flask request a mock DB session, and have the endpoint
        handle these fake requests
        """
        self.request = mock.MagicMock(spec=Request)
        self.session = mock.MagicMock(spec=Session)

        self._app = Flask(__name__)
        self._app.add_url_rule('/', view_func=JobsList.as_view(
            JobsList.__name__
        ))
        self._context = self._app.test_request_context()
        self._context.push()

    def tearDown(self) -> None:
        """
        Pop the testing context
        """
        self._context.pop()


class TestInit(TestJobList):
    """
    Contains unit tests for the ``__init__`` method of the endpoint
    """
    def test_init_no_job_list_provided(self):
        """
        Tests that if the endpoint does not have a job list, that a job list
        will be created
        """
        endpoint = JobsList(self.session, self.request)
        self.assertIsInstance(endpoint.job_list, JobListInterface)

    @given(job_lists())
    def test_init_job_list_provided(self, job_list: JobListInterface) -> None:
        """
        Tests that if the job list is provided, that it gets assigned
        correctly

        :param job_list: The randomly-generated job list to expose
        """
        endpoint = JobsList(self.session, self.request, job_list)
        self.assertEqual(endpoint.job_list, job_list)


class TestGet(TestJobList):
    """
    Contains unit tests for the ``GET`` request handler at this endpoint
    """
    @given(job_lists())
    def test_get(self, job_list: JobListInterface) -> None:
        """
        Tests that the endpoint returns the ``200`` status code for a valid
        list of jobs
        """
        endpoint = JobsList(self.session, self.request, job_list)
        response = endpoint.get()
        self.assertEqual(200, response.status_code)
        self.assert_data_equal(
            json.loads(response.data.decode('utf-8')),
            job_list
        )

    def assert_data_equal(
            self, data: dict, job_list: JobListInterface
    ) -> None:
        """
        Assert that the data is correctly displayed
        :param data: The data to retrieve
        :param job_list: The list of jobs to serialize
        """
        self.assertEqual(
            data['data'],
            self.serialize_jobs(job_list)
        )

    @staticmethod
    def serialize_jobs(job_list: JobListInterface) -> dict:
        serializer = JobOverview()
        return serializer.dump(job_list, many=True).data

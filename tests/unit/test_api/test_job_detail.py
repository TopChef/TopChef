"""
Contains unit tests for the ``/jobs/<job_id>`` endpoint
"""
import unittest
import unittest.mock as mock
from jsonschema import Draft4Validator, ValidationError
from sqlalchemy.orm import Session
from flask import Request, Flask
from hypothesis import given, assume
from hypothesis.strategies import sampled_from, dictionaries, text
from tests.unit.model_generators.job import jobs
from topchef.api.job_detail import JobDetail
from topchef.models import Job


class TestJobDetail(unittest.TestCase):
    """
    Base class for unit testing the ``NextJob`` endpoint
    """
    def setUp(self) -> None:
        """
        Set up the test
        """
        self.session = mock.MagicMock(spec=Session)
        self.request = mock.MagicMock(spec=Request)
        app = Flask(__name__)
        app.add_url_rule(
            '/', view_func=JobDetail.as_view(
                JobDetail.__name__,
            )
        )
        self.context = app.test_request_context()
        self.context.push()

    def tearDown(self) -> None:
        """
        Pop the context
        """
        self.context.pop()


class TestGet(TestJobDetail):
    """
    Contains unit tests for the get method
    """
    @given(jobs())
    def test_get(self, job: Job) -> None:
        """

        :param job: The randomly-generated job to test
        """
        endpoint = JobDetail(self.session, self.request)
        response = endpoint.get(job)
        self.assertEqual(200, response.status_code)


class TestPatch(TestJobDetail):
    """
    Contains unit tests for the ``patch`` method
    """
    _JOB_STATUS_LOOKUP = {
        Job.JobStatus.REGISTERED: "REGISTERED",
        Job.JobStatus.ERROR: "ERROR",
        Job.JobStatus.WORKING: "WORKING",
        Job.JobStatus.COMPLETED: "COMPLETED"
    }

    @given(
        jobs(),
        sampled_from(Job.JobStatus)
    )
    def test_patch_set_status(
            self, job: Job, status: Job.JobStatus
    ) -> None:
        """

        :param job: The randomly-generated job to modify
        :param status: The randomly-generated status to set
        """
        request_body = {
            'status': self._JOB_STATUS_LOOKUP[status]
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = JobDetail(self.session, flask_request=self.request)
        response = endpoint.patch(job)
        self.assertEqual(200, response.status_code)
        self.assertEqual(job.status, status)

    @given(
        jobs()
    )
    def test_patch_job_status_none(self, job: Job) -> None:
        """
        Tests that the job status is not changed if the desired status is
            None

        :param job: The randomly-generated job to modify
        """
        old_status = job.status
        request_body = {
            'status': None
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = JobDetail(self.session, flask_request=self.request)
        response = endpoint.patch(job)
        self.assertEqual(200, response.status_code)
        self.assertEqual(old_status, job.status)

    @given(
        jobs(),
        dictionaries(text(), text())
    )
    def test_patch_set_results_schema_matches(
            self,
            job: Job,
            new_results: dict
    ) -> None:
        """
        Tests that the results can be set correctly if they pass JSON schema
        validation
        """
        request_body = {
            'results': new_results
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        validator = mock.MagicMock(spec=Draft4Validator)
        validator.is_valid = mock.MagicMock(return_value=True)

        endpoint = JobDetail(
            self.session,
            flask_request=self.request,
            validator_factory=mock.MagicMock(return_value=validator)
        )
        response = endpoint.patch(job)
        self.assertEqual(200, response.status_code)
        self.assertEqual(job.results, new_results)

    @given(
        jobs()
    )
    def test_patch_set_results_are_none(
            self,
            job: Job
    ) -> None:
        """
        Tests that the endpoint allows a result of null to be sent in
        :param job: The randomly-generated job to modify
        """
        old_results = job.results
        request_body = {
            'results': None
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = JobDetail(
            self.session,
            flask_request=self.request
        )
        response = endpoint.patch(job)
        self.assertEqual(200, response.status_code)
        self.assertEqual(old_results, job.results)

    @given(
        jobs()
    )
    def test_patch_both_status_and_results_are_none(self, job: Job) -> None:
        """
        Tests that the endpoint doesn't modify the job status or the job
        results if they are both None

        :param job: The randomly-generated job to modify
        """
        old_results = job.results
        old_status = job.status

        request_body = {
            'status': None,
            'results': None
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = JobDetail(
            self.session,
            flask_request=self.request
        )
        response = endpoint.patch(job)
        self.assertEqual(200, response.status_code)
        self.assertEqual(old_results, job.results)
        self.assertEqual(old_status, job.status)

    @given(
        jobs(),
        dictionaries(text(), text())
    )
    def test_patch_results_do_not_match(
            self, job: Job, bad_results: dict
    ) -> None:
        """

        Tests that an exception is raised if an attempt is made to post
        results that do not match the result schema

        :param job: A randomly-generated job that will be the subject of
            this test
        :param bad_results: The invalid results to be rejected by the API
        """
        request_body = {
            'results': bad_results
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        validator = mock.MagicMock(spec=Draft4Validator)
        validator.is_valid = mock.MagicMock(return_value=False)
        validator.iter_errors = mock.MagicMock(
            return_value=iter({mock.MagicMock(spec=ValidationError)})
        )

        endpoint = JobDetail(
            self.session,
            flask_request=self.request,
            validator_factory=mock.MagicMock(return_value=validator)
        )

        with self.assertRaises(endpoint.Abort):
            endpoint.patch(job)

    @given(
        jobs(),
        text()
    )
    def test_patch_serialization_error(
            self, job: Job, bad_status: str
    ) -> None:
        """
        Tests that if an invalid entry is placed into the status entry,
        that an exception is thrown. This is testing the branch of the code
        that checks that the marshmallow serializer correctly reports bad data.

        :param job: The job to modify
        :param bad_status: An illegal job status to be caught by the
            marshmallow serializer
        """
        assume(bad_status not in self._JOB_STATUS_LOOKUP.values())
        request_body = {'status': bad_status}

        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = JobDetail(self.session, flask_request=self.request)

        with self.assertRaises(endpoint.Abort):
            endpoint.patch(job)

        self.assertTrue(endpoint.errors)

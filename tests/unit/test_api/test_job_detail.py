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
        :return:
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
        sampled_from(Job.JobStatus),
        dictionaries(text(), text())
    )
    def test_patch_happy_path(
            self, job: Job, status: Job.JobStatus, results: dict
    ) -> None:
        """

        :param job: The randomly-generated job to modify
        :param status: The randomly-generated status to set
        """
        request_body = {
            'status': self._JOB_STATUS_LOOKUP[status],
            'results': results
        }
        self.request.get_json = mock.MagicMock(return_value=request_body)
        endpoint = JobDetail(self.session, flask_request=self.request)
        response = endpoint.patch(job)
        self.assertEqual(200, response.status_code)
        self.assertEqual(job.status, status)
        self.assertEqual(job.results, results)

    @given(
        jobs(),
        dictionaries(text(), text())
    )
    def test_patch_serialization_error(
            self, job: Job, bad_results: dict
    ) -> None:
        """

        :param job: The job to modify
        :param bad_results: The illegal JSON for which errors are to be
            reported
        """
        assume('status' not in bad_results.keys())
        assume('results' not in bad_results.keys())
        self.request.get_json = mock.MagicMock(return_value=bad_results)
        endpoint = JobDetail(self.session, flask_request=self.request)

        with self.assertRaises(endpoint.Abort):
            endpoint.patch(job)

        self.assertTrue(endpoint.errors)

    @given(
        jobs(),
        sampled_from(Job.JobStatus),
        dictionaries(text(), text())
    )
    def test_patch_validation_error(
            self, job: Job, new_status: Job.JobStatus, bad_results: dict
    ) -> None:
        """

        :param job:
        :param bad_results:
        :return:
        """
        validator = mock.MagicMock(spec=Draft4Validator)
        validator.is_valid = mock.MagicMock(return_value=False)
        validator.iter_errors = mock.MagicMock(
            return_value=iter([ValidationError("Error")])
        )
        validator_factory = mock.MagicMock(spec=type, return_value=validator)

        self.request.get_json = mock.MagicMock(
            return_value={
                'status': self._JOB_STATUS_LOOKUP[new_status],
                'results': bad_results
            }
        )

        endpoint = JobDetail(
            self.session, validator_factory=validator_factory,
            flask_request=self.request
        )

        with self.assertRaises(endpoint.Abort):
            endpoint.patch(job)

        self.assertTrue(endpoint.errors)

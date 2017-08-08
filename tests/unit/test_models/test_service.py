"""
Contains unit tests for :mod:`topchef.models.service.Service`
"""
import unittest
import unittest.mock as mock
from topchef.models.service import Service
from sqlalchemy.orm import Session
from topchef.database.models import Service as DatabaseService
from topchef.models import JobList as JobListInterface
from hypothesis.strategies import text, booleans, dictionaries
from hypothesis import given


class TestService(unittest.TestCase):
    """
    Base class for unit tests of :class:`topchef.models.Service
    """
    def setUp(self):
        self.database_service = mock.MagicMock(
            spec=DatabaseService
        )  # type: DatabaseService

        self.service = Service(self.database_service)


class TestID(TestService):
    def test_get_id(self):
        self.assertEqual(self.service.id, self.database_service.id)


class TestName(TestService):
    @given(text())
    def test_setting_name_changes_it(self, name: str) -> None:
        self.service.name = name
        self.assertEqual(name, self.service.name)
        self.assertEqual(name, self.database_service.name)


class TestDescription(TestService):
    @given(text())
    def test_setting_description_changes_it(self, description: str):
        self.service.description = description
        self.assertEqual(description, self.service.description)
        self.assertEqual(description, self.database_service.description)


class TestJobRegistrationSchema(TestService):
    def test_job_registration_schema(self):
        self.assertEqual(
            self.service.job_registration_schema,
            self.database_service.job_registration_schema
        )


class TestJobResultSchema(TestService):
    def test_job_result_schema(self):
        self.assertEqual(
            self.service.job_result_schema,
            self.database_service.job_result_schema
        )


class TestIsServiceAvailable(TestService):
    @given(booleans())
    def test_setting_is_service_available_changes_it(self, boolean):
        self.service.is_service_available = boolean
        self.assertEqual(self.service.is_service_available, boolean)
        self.assertEqual(self.database_service.is_service_available, boolean)


class TestNew(TestService):
    """
    Contains unit tests for :meth:`topchef.models.Service.new`
    """
    def setUp(self):
        TestService.setUp(self)
        self.session = mock.MagicMock(spec=Session)  # type: Session

    @given(
        text(),
        text(),
        dictionaries(text(), text()),
        dictionaries(text(), text())
    )
    def test_creating_new_services(
            self, name: str, description: str,
            registration_schema: dict, result_schema: dict
    ):
        new_service = Service.new(
            name, description, registration_schema, result_schema, self.session
        )
        self.assertEqual(new_service.description, description)
        self.assertEqual(new_service.name, name)
        self.assertEqual(new_service.job_result_schema, result_schema)
        self.assertEqual(
            new_service.job_registration_schema, registration_schema
        )


class TestNewJob(TestService):
    def setUp(self):
        TestService.setUp(self)
        self.job_constructor = mock.MagicMock(spec=type)
        self.job_constructor.new = mock.MagicMock()

    @given(dictionaries(text(), text()))
    def test_creating_a_new_job(self, parameters: dict) -> None:
        new_job = self.service.new_job(parameters, self.job_constructor)
        self.assertEqual(
            new_job.db_model,
            self.job_constructor(self.service.db_model, parameters)
        )


class TestJobs(TestService):
    """
    Contains unit tests for the ``jobs`` property in the service model.
    """
    def setUp(self) -> None:
        """
        Overload the getter for SQLAlchemy sessions for a given database
        model with a mock. This method should work similarly to
        ``Session.object_session``, which returns the SQLAlchemy ORM session
        to which the model class is bound
        """
        TestService.setUp(self)
        self.session_getter = mock.MagicMock(spec=Session.object_session)
        self.service = Service(
            self.database_service, session_getter_for_model=self.session_getter
        )

    def test_jobs(self) -> None:
        """
        Tests that the session getter is called correctly when instantiating
        the job list. Tests that the job list that is returned implements the
        ``JobListInterface``.
        """
        jobs = self.service.jobs
        self.assertIsInstance(jobs, JobListInterface)
        self.assertEqual(
            mock.call(self.database_service),
            self.session_getter.call_args
        )

"""
Contains unit tests for :mod:`topchef.models.service.Service`
"""
import unittest
import unittest.mock as mock
from freezegun import freeze_time
from datetime import timedelta, datetime
from topchef.models.service import Service
from sqlalchemy.orm import Session
from topchef.database.models import Service as DatabaseService
from topchef.models import JobList as JobListInterface
from hypothesis.strategies import text, booleans, dictionaries, composite
from hypothesis.strategies import timedeltas
from hypothesis import given, assume
from tests.unit.database_model_generators import services as service_generator


class TestService(unittest.TestCase):
    """
    Base class for unit tests of :class:`topchef.models.Service
    """
    def setUp(self) -> None:
        self.database_service = mock.MagicMock(
            spec=DatabaseService
        )  # type: DatabaseService

        self.session_getter = mock.MagicMock(spec=Session.object_session)
        self.service = Service(self.database_service,
                               session_getter_for_model=self.session_getter)

    @staticmethod
    @composite
    def services(draw, db_services=service_generator()) -> Service:
        """

        :param draw: A function provided by hypothesis, that explains how to
         draw from hypothesis strategies
        :param db_services: The strategy used to generate database models
            representing services
        :return: An instance of the model service
        """
        return Service(draw(db_services))


class TestID(TestService):
    """
    Contains unit tests for the ``id`` property of the service
    """
    @given(service_generator())
    def test_get_id(self, db_service: DatabaseService) -> None:
        """
        Tests that a service model takes on the ID of its database model

        :param db_service: A randomly-generated DatabaseService
        """
        service = Service(db_service)
        self.assertEqual(service.id, db_service.id)


class TestName(TestService):
    """
    Contains unit tests for the ``name`` getter and setter
    """
    @given(text(), service_generator())
    def test_setting_name_changes_the_models(
            self, name: str, db_service: DatabaseService
    ) -> None:
        """
        Tests that setting a name on the service changes the name on the
            underlying database service

        :param name: The new name
        :param db_service: The new database service
        """
        service = Service(db_service)
        service.name = name
        self.assertEqual(name, service.name)
        self.assertEqual(name, db_service.name)


class TestDescription(TestService):
    """
    Contains unit tests for the ``description`` getter and setter
    """
    @given(text(), service_generator())
    def test_setting_description_changes_models(
            self, description: str, db_service: DatabaseService
    ) -> None:
        """
        Tests that setting the description on the service model class will
        also set the description on the underlying database service

        :param description: The description to set
        :param db_service: The randomly-generated database service
        """
        service = Service(db_service)
        service.description = description
        self.assertEqual(description, service.description)
        self.assertEqual(description, db_service.description)


class TestJobRegistrationSchema(TestService):
    @given(service_generator())
    def test_job_registration_schema(
            self, db_service: DatabaseService
    ) -> None:
        service = Service(db_service)
        self.assertEqual(
            service.job_registration_schema, db_service.job_registration_schema
        )

    @given(dictionaries(text(), text()), TestService.services())
    def test_unable_to_set_job_schema(
            self, new_reg: dict, service: DatabaseService
    ) -> None:
        """

        Tests that the ``job_registration_schema`` for the service is immutable

        :param new_reg: The registration schema to set
        :param service: The randomly generated service for which the
            property is attempted to be set
        """
        with self.assertRaises(AttributeError):
            service.job_registration_schema = new_reg


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


class TestHasTimedOut(TestService):
    @given(
        timedeltas(min_delta=timedelta(seconds=0.01)),
        timedeltas(min_delta=timedelta(seconds=0))
    )
    def test_has_timed_out_true(
            self, timeout: timedelta, time_to_wait: timedelta
    ) -> None:
        """

        :param timeout: The timeout to set and wait for
        :param time_to_wait: The time to wait on top of the timeout,
             in order to ensure that the server timed out
        :return:
        """
        self.service.timeout = timeout
        self.service.check_in()

        assume(
            self._target_time_in_range(
                datetime.utcnow(), timeout, time_to_wait
            )
        )

        time_to_freeze_to = datetime.utcnow() + timeout + time_to_wait

        with freeze_time(time_to_freeze_to):  # ZA WARUDO!
            self.assertTrue(self.service.has_timed_out)

    @given(
        timedeltas(min_delta=timedelta(seconds=0.01)),
        timedeltas(max_delta=timedelta(seconds=-0.01))
    )
    def test_has_timed_out_false(
            self, timeout: timedelta, time_to_wait: timedelta
    ) -> None:
        self.service.timeout = timeout
        self.service.check_in()

        assume(
            self._target_time_in_range(
                datetime.utcnow(), timeout, time_to_wait
            )
        )

        with freeze_time(
            datetime.utcnow() + timeout + time_to_wait
        ):  # ZA WARUDO!
            self.assertFalse(self.service.has_timed_out)

    @staticmethod
    def _target_time_in_range(
            base: datetime, timeout: timedelta, time_to_wait: timedelta
    ) -> bool:
        try:
            base + timeout + time_to_wait
            return True
        except OverflowError:
            return False


class TestTimeout(TestService):
    """
    Contains unit tests for the ``timeout`` property
    """
    @given(timedeltas(min_delta=timedelta(microseconds=1)))
    def test_that_setting_valid_timeout_changes_it(
            self, timeout: timedelta
    ):
        self.service.timeout = timeout
        self.assertEqual(
            timeout.total_seconds(), self.service.timeout.total_seconds()
        )

    @given(timedeltas(max_delta=timedelta(microseconds=0)))
    def test_setting_invalid_timeout(self, timeout: timedelta) -> None:
        with self.assertRaises(ValueError):
            self.service.timeout = timeout


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

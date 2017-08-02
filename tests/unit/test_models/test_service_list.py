"""
Contains unit tests for :mod:`topchef.models.service_list
"""
from unittest import TestCase
from unittest.mock import MagicMock, call
from uuid import UUID
from sqlalchemy.orm import Session
from topchef.models.service_list import ServiceList
from topchef.models.service import Service
from topchef.database.models import Service as DatabaseService
from topchef.database.models import Job as DatabaseJob
from hypothesis import given
from hypothesis.strategies import text, booleans
from random import randint


class TestServiceList(TestCase):
    """
    Contains unit tests for the service list
    """
    def setUp(self) -> None:
        """
        Create a mock DB session, and make the service list use this mock
        session for testing
        """
        self.db_session = MagicMock(spec=Session)  # type: Session
        self.service_list = ServiceList(self.db_session)
        self.service_id = MagicMock(spec=UUID)  # type: UUID

    @property
    def db_model(self):
        return self.db_session.query(DatabaseService).filter_by(
            id=self.service_id
        ).first()


class TestGetItem(TestServiceList):
    """
    Contains unit tests for :mod:`topchef.models.ServiceList.__getitem__`
    """
    def test_getitem(self) -> None:
        """
        Test that the model is queried correctly, and
        """
        service = self.service_list[self.service_id]
        self.assertEqual(
            service,
            Service(self.db_model)
        )


class TestSetItem(TestServiceList):
    """
    Contains unit tests for the services setter
    """
    @given(text())
    def test_set_description(self, description):
        service = self.service_list[self.service_id]
        service.description = description
        self.service_list[self.service_id] = service

        self.assertEqual(call(self.db_model), self.db_session.add.call_args)
        self.assertEqual(self.db_model.description, description)

    @given(text())
    def test_set_name(self, name):
        service = self.service_list[self.service_id]
        service.name = name
        self.service_list[self.service_id] = service

        self.assertEqual(call(self.db_model), self.db_session.add.call_args)
        self.assertEqual(self.db_model.name, name)

    @given(booleans())
    def test_set_is_available(self, is_available: bool):
        service = self.service_list[self.service_id]
        service.is_service_available = is_available
        self.service_list[self.service_id] = service

        self.assertEqual(call(self.db_model), self.db_session.add.call_args)


class TestDelItem(TestServiceList):
    def setUp(self):
        TestServiceList.setUp(self)
        self.job = MagicMock(spec=DatabaseJob)

        self.db_model.jobs = [self.job]

    def test_delitem_service_deleted(self):
        del self.service_list[self.service_id]
        self.assertEqual(
            call(self.db_model),
            self.db_session.delete.call_args
        )

    def test_delitem_job_deleted(self):
        del self.service_list[self.service_id]
        self.assertIn(
            call(self.job),
            self.db_session.delete.call_args_list
        )


class TestContains(TestServiceList):
    def setUp(self):
        TestServiceList.setUp(self)
        self.service = self.service_list[self.service_id]

    def test_contains_service_id(self):
        self.assertIn(self.service_id, self.service_list)

    def test_contains_service(self):
        self.assertIn(self.service, self.service_list)


class TestLen(TestServiceList):
    def test_len(self):
        self.assertEqual(
            int(self.db_session.query().count()), len(self.service_list)
        )


class TestNew(TestServiceList):
    def setUp(self):
        TestServiceList.setUp(self)
        self.name = MagicMock(spec=str)
        self.description = MagicMock(spec=str)
        self.registration_schema = MagicMock(spec=dict)
        self.result_schema = MagicMock(spec=dict)

    def test_new(self):
        service = self.service_list.new(
            self.name, self.description, self.registration_schema,
            self.result_schema
        )
        self.assertEqual(
            service.description, self.description
        )
        self.assertEqual(
            self.name, service.name
        )
        self.assertEqual(
            self.registration_schema, service.job_registration_schema
        )
        self.assertEqual(
            self.result_schema, service.job_result_schema
        )
        self.assertEqual(call(service.db_model), self.db_session.add.call_args)

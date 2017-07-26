import os
from uuid import uuid4
from unittest import TestCase
from abc import ABCMeta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from topchef.models import Service
from topchef.database.schemas import DatabaseSchemaWithJSONTable
from topchef.storage import RelationalDatabaseStorage


class IntegrationTestCase(TestCase, metaclass=ABCMeta):
    """
    Base class for integration tests
    """
    DATABASE_ENVIRONMENT_VARIABLE_KEY = 'DATABASE_URI'
    SQLITE_IN_MEMORY_URI = 'sqlite://'

    def setUp(self) -> None:
        TestCase.setUp(self)
        self.database_uri = os.environ.get(
            self.DATABASE_ENVIRONMENT_VARIABLE_KEY,
            default=self.SQLITE_IN_MEMORY_URI
        )
        self.engine = create_engine(self.database_uri)
        self.session_factory = sessionmaker(bind=self.engine)
        self.database = DatabaseSchemaWithJSONTable()
        self.database.metadata.create_all(bind=self.engine)

        self.storage = RelationalDatabaseStorage(self.session_factory)

    def tearDown(self):
        self.database.metadata.drop_all(bind=self.engine)


class IntegrationTestCaseWithService(IntegrationTestCase, metaclass=ABCMeta):
    """
    Base class for integration tests, with a service already built
    """

    @classmethod
    def setUpClass(cls):
        IntegrationTestCase.setUpClass()
        cls.service_id = uuid4()
        cls.service_name = 'Service'
        cls.service_description = 'description'

        cls.job_registration_schema = {
            'type': 'object',
            'properties': {
                'value': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 10
                }
            }
        }

        cls.valid_job_registration_schema = {'value': 5}
        cls.invalid_job_registration_schema = {'value': 11}

        cls.job_result_schema = {
            'type': 'object',
            'properties': {
                'result': {
                    'type': 'integer',
                    'minimum': 11,
                    'maximum': 21
                }
            }
        }

        cls.valid_result_schema = {'result': 16}
        cls.invalid_result_schema = {'result': 2123213}

        cls.service = Service(
            cls.service_id, cls.service_name, cls.service_description,
            cls.job_registration_schema, cls.job_result_schema
        )

    def setUp(self):
        IntegrationTestCase.setUp(self)
        db_session = self.session_factory()
        self.service.write(db_session, self.storage)

    def tearDown(self):
        self.service.delete(self.session_factory(), self.storage)
        IntegrationTestCase.tearDown(self)

import os
from unittest import TestCase
from abc import ABCMeta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from topchef.database.schemas import DatabaseSchema


class IntegrationTestCase(TestCase, metaclass=ABCMeta):
    """
    Base class for integration tests
    """
    DATABASE_ENVIRONMENT_VARIABLE_KEY = 'DATABASE_URI'
    SQLITE_IN_MEMORY_URI = 'sqlite://'

    @classmethod
    def setUpClass(cls) -> None:
        TestCase.setUpClass()
        cls.database_uri = os.environ.get(
            cls.DATABASE_ENVIRONMENT_VARIABLE_KEY,
            default=cls.SQLITE_IN_MEMORY_URI
        )
        cls.engine = create_engine(cls.database_uri)
        cls.session = Session(bind=cls.engine, expire_on_commit=False)
        cls.database = DatabaseSchema()
        cls.database.metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, 'session'):
            cls.session.commit()
        if hasattr(cls, 'database') and hasattr(cls, 'engine'):
            cls.database.metadata.drop_all(bind=cls.engine)

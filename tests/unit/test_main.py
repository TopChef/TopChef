"""
Contains unit tests for :mod:`topchef.__main__`
"""
import unittest
import unittest.mock as mock
from flask import Flask
from topchef.__main__ import TopchefManager
from topchef.wsgi_app import DatabaseEngineFactory, WSGIAppFactory
from topchef.database import DatabaseSchema


class TestMain(unittest.TestCase):
    """
    Base class for unit testing the command line runner.
    """
    def setUp(self) -> None:
        """

        Create a mock application factory and send it to the CLI runner
        """
        self.db_engine_factory = mock.MagicMock(spec=DatabaseEngineFactory)
        self.app_constructor = mock.MagicMock(spec=WSGIAppFactory)
        self.manager = TopchefManager(
            self.app_constructor, self.db_engine_factory
        )


class TestRun(TestMain):
    """
    Contains unit tests for the ``Run`` command in the command line manager
    """
    def setUp(self) -> None:
        """

        Set up the unit test by extracting the run command from the command
        line manager
        """
        TestMain.setUp(self)
        self.app = mock.MagicMock(spec=Flask)
        self.command = self.manager.Run(self.app)

    def test_run(self) -> None:
        """

        Tests that running the ``run`` command correctly calls the ``run``
        method of the flask application
        """
        self.command.run()
        self.assertTrue(self.app.run.called)


class TestCreateDB(TestMain):
    """
    Contains unit tests for the ``create_db`` command
    """
    def setUp(self) -> None:
        """
        Create a mock instance of the ``CreateDB`` type, and provide a mock
        database schema to create
        """
        TestMain.setUp(self)
        self.database_schema = mock.MagicMock(spec=DatabaseSchema)
        self.command = self.manager.CreateDB(
            self.db_engine_factory, self.database_schema
        )

    def test_run(self) -> None:
        """

        Tests that the ``create-db`` command works correctly
        """
        self.command.run()
        self.assertEqual(
            mock.call(bind=self.db_engine_factory.engine),
            self.database_schema.metadata.create_all.call_args
        )

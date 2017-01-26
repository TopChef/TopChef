"""
Contains unit tests for :mod:`topchef`
"""
import abc
import os
import pytest
from topchef.config import Config
from sqlalchemy import create_engine
from topchef.database import METADATA
from topchef.api_server import app


class UnitTest(object):
    """
    Base class for all unit tests
    """
    __metaclass__ = abc.ABCMeta
    headers = {'Content-Type': 'application/json'}

    @abc.abstractproperty
    def endpoint(self):
        """
        :return: The API endpoint which is being tested. Inheritors must
        overload this.
        """
        raise NotImplementedError()

    @pytest.fixture(scope='session')
    def _app_config(self):
        """
        Creates a fake configuration object to share
        :return: A fake config
        """
        config = Config()
        return config

    @pytest.yield_fixture(scope='session')
    def _schema_directory(self, _app_config):
        if not os.path.isdir(_app_config.SCHEMA_DIRECTORY):
            os.mkdir(_app_config.SCHEMA_DIRECTORY)

        yield

        if not os.listdir(_app_config.SCHEMA_DIRECTORY):
            os.rmdir(_app_config.SCHEMA_DIRECTORY)

    @pytest.fixture(scope='session')
    def _engine(self, _app_config):
        """
        :param _app_config: The configuration for which the engine is to be
            made
        :return: An engine for an in-memory SQLite database. This DB is
            flushed at the end of the test
        """
        engine = create_engine(_app_config.DATABASE_URI)

        return engine

    @pytest.yield_fixture(scope='session')
    def _database(self, _engine, _schema_directory):
        """
        Creates an in-memory SQLite database out of a given engine
        :param _engine: The engine
        """

        METADATA.create_all(bind=_engine)

        yield

        METADATA.drop_all(bind=_engine)

    @pytest.fixture
    def _app(self, _database, _app_config):
        """
        Create a mock app
        :param _database:
        :param _app_config:
        :return:
        """
        app.config.update(_app_config.parameter_dict)
        return app

    @pytest.fixture
    def _app_client(self, _app):
        """
        Creates a test client for a given app, using the endpoint
        :param _app:
        :return:
        """
        client = _app.test_client()
        return client

"""
Contains a factory for making WSGI applications
"""
import abc
from flask import Flask
from .api import APIMetadata, ServicesList, ServiceDetail
from .api import JobsList, JobsForService, JobQueueForService
from .api import NextJob as NextJobEndpoint
from .method_override_middleware import HTTPMethodOverrideMiddleware
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from .config import config


class WSGIAppFactory(object, metaclass=abc.ABCMeta):
    """
    Factory for making the WSGI app
    """
    @property
    @abc.abstractmethod
    def app(self) -> Flask:
        raise NotImplementedError()


class DatabaseEngineFactory(object, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def engine(self) -> Engine:
        raise NotImplementedError()


class ProductionWSGIAppFactory(
    WSGIAppFactory, DatabaseEngineFactory
):
    """
    Factory for making the app
    """
    def __init__(self):
        self._app = Flask(__name__)
        self._app.wsgi_app = HTTPMethodOverrideMiddleware(self._app.wsgi_app)

        self._engine = create_engine(config.DATABASE_URI)

        self._app.add_url_rule(
            '/', view_func=APIMetadata.as_view(
                APIMetadata.__name__, self._session_factory()
            )
        )
        self._app.add_url_rule(
            '/services',
            view_func=ServicesList.as_view(
                ServicesList.__name__, self._session_factory()
            )
        )
        self._app.add_url_rule(
            '/services/<service_id>',
            view_func=ServiceDetail.as_view(
                ServiceDetail.__name__, self._session_factory()
            )
        )
        self._app.add_url_rule(
            '/services/<service_id>/jobs/queue',
            view_func=JobQueueForService.as_view(
                JobQueueForService.__name__, self._session_factory()
            )
        )
        self._app.add_url_rule(
            '/jobs',
            view_func=JobsList.as_view(
                JobsList.__name__, self._session_factory()
            )
        )
        self._app.add_url_rule(
            '/services/<service_id>/jobs',
            view_func=JobsForService.as_view(
                JobsForService.__name__, self._session_factory()
            )
        )
        self._app.add_url_rule(
            '/services/<service_id>/jobs/next',
            view_func=NextJobEndpoint.as_view(
                NextJobEndpoint.__name__, self._session_factory()
            )
        )

    @property
    def app(self) -> Flask:
        return self._app

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def _session_factory(self) -> sessionmaker:
        return sessionmaker(bind=self._engine)


class TestingWSGIAPPFactory(
    ProductionWSGIAppFactory, WSGIAppFactory, DatabaseEngineFactory
):
    pass

APP_FACTORY = ProductionWSGIAppFactory()

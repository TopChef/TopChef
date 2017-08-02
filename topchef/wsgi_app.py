"""
Contains a factory for making WSGI applications
"""
import abc
from flask import Flask
from .api import api
from .method_override_middleware import HTTPMethodOverrideMiddleware


class WSGIAppFactory(object, metaclass=abc.ABCMeta):
    """
    Factory for making the WSGI app
    """
    @property
    @abc.abstractmethod
    def app(self):
        raise NotImplementedError()


class APIFactory(object, metaclass=abc.ABCMeta):
    """
    Interface for making the Flask-REST-JSONAPI spec
    """
    @property
    @abc.abstractmethod
    def api(self):
        raise NotImplementedError()


class ProductionWSGIAppFactory(
    WSGIAppFactory, APIFactory
):
    """
    Factory for making the app
    """
    def __init__(self):
        self._app = Flask(__name__)
        self._app.wsgi_app = HTTPMethodOverrideMiddleware(self._app.wsgi_app)
        self._api = api
        self._api.init_app(self._app)

    @property
    def app(self):
        return self._app

    @property
    def api(self):
        return self._api


class TestingWSGIAPPFactory(
    ProductionWSGIAppFactory, WSGIAppFactory, APIFactory
):
    pass

APP_FACTORY = ProductionWSGIAppFactory()

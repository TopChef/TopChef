"""
Contains a factory for making WSGI applications
"""
import abc
from flask import Flask
from flask_rest_jsonapi import Api


class WSGIAppFactory(object, with_metaclass=abc.ABCMeta):
    """
    Factory for making the WSGI app
    """
    @abc.abstractmethod
    @property
    def app(self):
        raise NotImplementedError()



class APIFactory(object, with_metaclass=abc.ABCMeta):
    """
    Interface for making the Flask-REST-JSONAPI spec
    """
    @abc.abstractmethod
    @property
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
        self._api = Api(self._app)

    @property
    def app(self):
        return self._app

    @property
    def api(self):
        return self._api

APP_FACTORY = ProductionWSGIAppFactory()

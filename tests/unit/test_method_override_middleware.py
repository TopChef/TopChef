"""
Contains unit tests for :mod:`topchef.method_override_middleware``
"""
import pytest
import mock
from topchef.method_override_middleware import HTTPMethodOverrideMiddleware


@pytest.fixture()
def environ():
    return mock.MagicMock()


@pytest.fixture()
def start_response():
    return mock.MagicMock()


@pytest.fixture()
def app():
    return mock.MagicMock()


@pytest.fixture()
def middleware(app):
    return HTTPMethodOverrideMiddleware(app)


def test_constructor(middleware, app):
    assert middleware.app == app


def test_call_no_override(middleware, environ, start_response):
    environ.get = mock.MagicMock(return_value='')
    middleware(environ, start_response)

    assert environ.__setitem__.call_count == 0


def test_call_post_override(middleware, environ, start_response):
    environ.get = mock.MagicMock(return_value='POST')
    middleware(environ, start_response)

    assert environ.__setitem__.call_args == mock.call(
        "REQUEST_METHOD", b"POST")


def test_call_patch_override(middleware, environ, start_response):
    environ.get = mock.MagicMock(return_value="PATCH")
    middleware(environ, start_response)

    assert environ.__setitem__.call_args == mock.call(
        "REQUEST_METHOD", b"PATCH")


def test_bodyless_method(middleware, environ, start_response):
    environ.get = mock.MagicMock(return_value="GET")
    middleware(environ, start_response)

    assert environ.__setitem__.call_count == 2

    assert environ.__setitem__.call_args_list == [
        mock.call("REQUEST_METHOD", b"GET"),
        mock.call("CONTENT_LENGTH", b"0")
    ]

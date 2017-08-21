"""
Contains unit tests for :mod:`topchef.method_override_middleware``
"""
import unittest
import unittest.mock as mock
from topchef.method_override_middleware import HTTPMethodOverrideMiddleware
from flask import Flask


class TestMethodOverrideMiddleware(unittest.TestCase):
    """
    Base class for testing the HTTP method override middleware
    """
    def setUp(self) -> None:
        """

        :return:
        """
        self.environment = mock.MagicMock()
        self.start_response = mock.MagicMock()
        self.flask_app = mock.MagicMock(spec=Flask)
        self.http_middleware = HTTPMethodOverrideMiddleware(self.flask_app)


class TestInitializer(TestMethodOverrideMiddleware):
    """
    Contains unit tests for the method override middleware initializer
    """
    def test_app_was_set(self):
        """
        Test that the flask app was set
        """
        middleware = HTTPMethodOverrideMiddleware(self.flask_app)
        self.assertEqual(middleware.app, self.flask_app)


class TestCall(TestMethodOverrideMiddleware):
    """
    Contains unit tests for
    :meth:`topchef.method_override_middleware.HTTPMethodOverrideMiddleware
    .__call__`
    """
    def test_call_no_override(self):
        """
        Tests that if a method override is not specified, then no method
        overloading occurs in the request environment
        """
        self.environment.get = mock.MagicMock(return_value='')
        self.http_middleware(self.environment, self.start_response)
        self.assertEqual(0, self.environment.__setitem__.call_count)

    def test_call_post_override(self):
        """
        Tests that the request is successfully overridden to a ``POST``
        request if the header is provided in the request environment
        """
        self.environment.get = mock.MagicMock(return_value="POST")
        self.http_middleware(self.environment, self.start_response)
        self.assertEqual(
            mock.call("REQUEST_METHOD", 'POST'),
            self.environment.__setitem__.call_args
        )

    def test_call_patch_override(self):
        """
        Tests that requests can be successfully overridden to ``PATCH``
        requests if the header is provided in the request environment
        """
        self.environment.get = mock.MagicMock(return_value="PATCH")
        self.http_middleware(self.environment, self.start_response)
        self.assertEqual(
            mock.call("REQUEST_METHOD", 'PATCH'),
            self.environment.__setitem__.call_args
        )

    def test_bodyless_method(self):
        """
        Tests that the middleware sets the ``REQUEST_METHOD`` argument to
        the correct request method, and the ``CONTENT_LENGTH`` header to 0,
        when a request method without a body is sent in.
        """
        self.environment.get = mock.MagicMock(return_value="GET")
        self.http_middleware(self.environment, self.start_response)
        self.assertEqual(2, self.environment.__setitem__.call_count)
        self.assertEqual(
            [
                mock.call("REQUEST_METHOD", 'GET'),
                mock.call("CONTENT_LENGTH", '0')
            ],
            self.environment.__setitem__.call_args_list
        )

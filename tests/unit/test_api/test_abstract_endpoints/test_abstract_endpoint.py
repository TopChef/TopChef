"""
Contains unit tests for
"""
import json
import unittest
import unittest.mock as mock

from flask import Request, jsonify, Response, Flask
from sqlalchemy.orm import Session

from topchef.api.abstract_endpoints.abstract_endpoint import AbstractEndpoint
from topchef.models import APIError


class TestAbstractEndpoint(unittest.TestCase):
    """
    Contains unit tests for the abstract endpoint
    """
    def setUp(self) -> None:
        """

        Create a fake DB session and a fake request, and put them into the
        concrete endpoint
        """
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request
        self.endpoint = self.ConcreteGetEndpoint(
            self.session, self.request
        )

        self.app = Flask(__name__)
        self.app.add_url_rule(
            '/', view_func=self.ConcreteGetEndpoint.as_view(
                self.ConcreteGetEndpoint.__name__
            )
        )
        self._context = self.app.test_request_context()

        self._context.push()

    def tearDown(self) -> None:
        """
        Pop the request context
        """
        self._context.pop()

    class ConcreteGetEndpoint(AbstractEndpoint):
        """
        Contains an endpoint that implements a simple get endpoint
        """
        @staticmethod
        def get() -> Response:
            """

            :return: A mock response
            """
            return jsonify({'status': 'success'})

    class ConcretePatchEndpoint(AbstractEndpoint):
        def patch(self):
            return jsonify({'status': 'success'})

    class ConcretePostEndpoint(AbstractEndpoint):
        def post(self):
            return jsonify({'status': 'success'})

    class ConcretePutEndpoint(AbstractEndpoint):
        def put(self):
            return jsonify({'status': 'success'})

    class ConcreteDeleteEndpoint(AbstractEndpoint):
        def delete(self):
            return jsonify({'status': 'success'})

    class ConcreteGetEndpointWithAbort(AbstractEndpoint):
        """
        Contains an endpoint whose get method will throw an ``Abort`` exception
        """
        def get(self):
            raise self.Abort()

    class ConcreteEndpointWithArgument(AbstractEndpoint):
        """
        Contains an endpoint that takes in an argument, in order to test
        graceful HTTP status code 405 handling
        """
        def get(self, argument):
            return jsonify({'argument': argument, 'status': 'success'})


class TestInitAndNew(TestAbstractEndpoint):
    """
    Contains unit tests for ``__init__`` and ``__new__``
    """
    def test_new_get_endpoint(self) -> None:
        """
        Tests that an endpoint with a ``get`` method adds ``GET`` to its
        list of allowed methods
        """
        endpoint = self.ConcreteGetEndpoint(self.session, self.request)
        self.assertEqual(endpoint.database_session, self.session)
        self.assertIn('GET', endpoint.methods)

    def test_new_patch_endpoint(self):
        endpoint = self.ConcretePatchEndpoint(self.session, self.request)
        self.assertIn('PATCH', endpoint.methods)

    def test_new_post_endpoint(self):
        endpoint = self.ConcretePostEndpoint(self.session, self.request)
        self.assertIn('POST', endpoint.methods)

    def test_new_put_endpoint(self):
        endpoint = self.ConcretePutEndpoint(self.session, self.request)
        self.assertIn('PUT', endpoint.methods)

    def test_new_delete_endpoint(self):
        endpoint = self.ConcreteDeleteEndpoint(self.session, self.request)
        self.assertIn('DELETE', endpoint.methods)


class TestDispatchRequest(TestAbstractEndpoint):
    def setUp(self):
        TestAbstractEndpoint.setUp(self)
        self.request.method = 'GET'
        self.endpoint_without_get = self.ConcreteDeleteEndpoint(
            self.session, self.request
        )
        self.app.add_url_rule(
            '/delete', view_func=self.ConcreteDeleteEndpoint.as_view(
                self.ConcreteDeleteEndpoint.__name__
            )
        )
        self.app.add_url_rule(
            '/explosive_endpoint', view_func=self.ExplosiveGetEndpoint.as_view(
                self.ExplosiveGetEndpoint.__name__
            )
        )
        self.app.add_url_rule(
            '/explosive_append_endpoint',
            view_func=self.ExplosiveAppendEndpoint.as_view(
                self.ExplosiveAppendEndpoint.__name__
            )
        )
        self.app.add_url_rule(
            '/two_four_hundreds',
            view_func=self.TwoFourHundredExceptionEndpoint.as_view(
                self.TwoFourHundredExceptionEndpoint.__name__
            )
        )

        self.status_code_ok = 200
        self.status_code_test_error = 499

    def test_get_method_not_allowed(self) -> None:
        """
        Tests that a method that is not allowed will return error 405
        """
        response = self.endpoint_without_get.dispatch_request()
        self.assertEqual(response.status_code, 405)

    def test_get_no_method_error(self) -> None:
        """
        Tests that the happy path works correctly
        """
        response = self.endpoint.dispatch_request()
        self.assertEqual(self.status_code_ok, response.status_code)
        self.assertTrue(self.session.commit.called)

    def test_get_error_thrown_in_method(self) -> None:
        """
        Tests that the endpoint correctly reports reportable errors that
        were thrown during the endpoint execution
        """
        endpoint = self.ExplosiveGetEndpoint(self.session, self.request)
        response = endpoint.dispatch_request()
        self.assertEqual(self.status_code_test_error, response.status_code)
        self.assertIn(
            'errors', json.loads(response.data.decode('utf-8')).keys()
        )
        self.assertTrue(self.session.commit.called)

    def test_get_abort_exception_thrown(self) -> None:
        """
        Tests that the error is correctly handled if an ``Abort`` is thrown
        in the endpoint
        """
        endpoint = self.ConcreteGetEndpointWithAbort(
            self.session, self.request
        )
        response = endpoint.dispatch_request()
        self.assertEqual(500, response.status_code)
        self.assertIn(
            'errors', json.loads(response.data.decode('utf-8')).keys()
        )

    def test_get_error_appended_in_method(self) -> None:
        """
        Tests that an error response is returned
        """
        endpoint = self.ExplosiveAppendEndpoint(self.session, self.request)
        response = endpoint.dispatch_request()
        self.assertEqual(self.status_code_test_error, response.status_code)

    def test_two_400_exceptions(self):
        """
        Tests that appending two errors with different ``4XX`` series
        HTTP status codes will result in a single request that has a status
        code of ``400``.
        """
        endpoint = self.TwoFourHundredExceptionEndpoint(
            self.session, self.request
        )
        response = endpoint.dispatch_request()
        self.assertEqual(400, response.status_code)

    def test_500_exception(self):
        """
        Tests that having one ``4XX`` series status code and one ``5XX``
        series status code will result in an error of ``500``
        """
        endpoint = self.FiveHundredExceptionEndpoint(
            self.session, self.request
        )
        response = endpoint.dispatch_request()
        self.assertEqual(500, response.status_code)

    def test_get_method_not_allowed_handler(self):
        self.app.add_url_rule(
            '/<argument>',
            view_func=self.ConcreteEndpointWithArgument.as_view(
                self.ConcreteEndpointWithArgument.__name__
            )
        )
        self.request.method = 'POST'
        endpoint = self.ConcreteEndpointWithArgument(
            self.session, self.request
        )
        response = endpoint.dispatch_request()
        self.assertEqual(405, response.status_code)

    class ExplosiveGetEndpoint(AbstractEndpoint):
        """
        Contains an endpoint that is going to throw a reportable API exception
        """
        def __init__(self, session, request):
            super(TestDispatchRequest.ExplosiveGetEndpoint, self).__init__(
                session, request
            )

        def get(self) -> Response:
            raise TestDispatchRequest.ConcreteAPIError()

    class ConcreteAPIError(APIError):
        """
        A generic reportable API exception
        """
        def __init__(self, status_code=499):
            self._status_code = status_code

        @property
        def title(self) -> str:
            """

            :return: The title of the exception
            """
            return 'Concrete API Exception'

        @property
        def detail(self) -> str:
            """

            :return: A detailed error message
            """
            return 'The endpoint exploded. This is good for testing'

        @property
        def status_code(self) -> int:
            """

            :return: The HTTP status code to throw
            """
            return self._status_code

    class ExplosiveAppendEndpoint(AbstractEndpoint):
        """
        An endpoint that appends an exception to the error list
        """
        def get(self) -> Response:
            self.errors.append(TestDispatchRequest.ConcreteAPIError())
            return jsonify({
                'status':
                    "If you're reading this from the API, you dun goofed!"
            })

    class TwoFourHundredExceptionEndpoint(AbstractEndpoint):
        """
        Describes an endpoint that throws two ``4XX`` series errors
        """
        def get(self) -> Response:
            self.errors.append(
                TestDispatchRequest.ConcreteAPIError(499)
            )
            self.errors.append(
                TestDispatchRequest.ConcreteAPIError(431)
            )
            return jsonify(dict())

    class FiveHundredExceptionEndpoint(AbstractEndpoint):
        def get(self) -> Response:
            self.errors.append(
                TestDispatchRequest.ConcreteAPIError(499)
            )
            self.errors.append(
                TestDispatchRequest.ConcreteAPIError(501)
            )
            return jsonify(dict())

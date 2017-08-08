"""
Contains unit tests for
"""
import unittest
import unittest.mock as mock
from flask import Request, jsonify, Response, Flask
from sqlalchemy.orm import Session
from topchef.api.abstract_endpoint import AbstractEndpoint


class TestAbstractEndpoint(unittest.TestCase):
    """
    Contains unit tests for the abstract endpoint
    """
    def setUp(self) -> None:
        """

        Create a fake DB session and a fake request, and put them into the
        concrete endpoint
        """
        self.session = mock.MagicMock(spec=Session)
        self.request = mock.MagicMock(spec=Request)
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
        self.assertEqual(endpoint.methods, ['OPTIONS', 'HEAD', 'GET'])

    def test_new_patch_endpoint(self):
        endpoint = self.ConcretePatchEndpoint(self.session, self.request)
        self.assertEqual(endpoint.methods, ['OPTIONS', 'HEAD', 'PATCH'])

    def test_new_post_endpoint(self):
        endpoint = self.ConcretePostEndpoint(self.session, self.request)
        self.assertEqual(endpoint.methods, ['OPTIONS', 'HEAD', 'POST'])

    def test_new_put_endpoint(self):
        endpoint = self.ConcretePutEndpoint(self.session, self.request)
        self.assertEqual(endpoint.methods, ['OPTIONS', 'HEAD', 'PUT'])

    def test_new_delete_endpoint(self):
        endpoint = self.ConcreteDeleteEndpoint(self.session, self.request)
        self.assertEqual(endpoint.methods, ['OPTIONS', 'HEAD', 'DELETE'])


class TestDispatchRequest(TestAbstractEndpoint):
    def setUp(self):
        TestAbstractEndpoint.setUp(self)
        self.endpoint_without_get = self.ConcreteDeleteEndpoint(
            self.session, self.request
        )
        self.app.add_url_rule(
            '/delete', view_func=self.ConcreteDeleteEndpoint.as_view(
                self.ConcreteDeleteEndpoint.__name__
            )
        )

    def test_get_method_not_allowed(self) -> None:
        """
        Tests that a method that is not allowed will return error 405
        """
        self.request.method = 'GET'
        response = self.endpoint_without_get.dispatch_request()
        self.assertEqual(response.status_code, 405)

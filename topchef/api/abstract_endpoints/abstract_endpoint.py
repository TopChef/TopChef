"""
Provides an abstract endpoint unique to this API from which all other
endpoints will inherit. This takes care of managing the database session,
as well as providing a ``links`` object containing the endpoint to itself.
"""
from functools import reduce
from flask import Response, jsonify
from flask.views import View, http_method_funcs
from flask import url_for, Request
from flask import request as flask_request
from sqlalchemy.orm import Session
import abc
from typing import List, Iterable, Callable, Optional, Any, Set
from topchef.models import APIError
from topchef.models.errors import MethodNotAllowedError
from topchef.models.errors import SQLAlchemyError
from topchef.models.errors import RequestNotJSONError
from topchef.serializers import APIException as ExceptionSerializer
from topchef.serializers import JSONSchema

__all__ = ['AbstractEndpoint']


class AbstractMethodViewType(abc.ABCMeta):
    """
    Maps the class for abstract method views
    """
    def __new__(mcs, name, bases, namespace: dict) -> type:
        if 'methods' not in namespace.keys():
            namespace['methods'] = mcs._get_methods_from_bases(bases)
            namespace['methods'].extend(
                mcs._get_methods_from_namespace(namespace)
            )

        return abc.ABCMeta.__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace: dict) -> None:
        super(AbstractMethodViewType, cls).__init__(name, bases, namespace)

    @staticmethod
    def _get_methods_from_bases(bases: Iterable[type]):
        available_methods = set()
        for base in bases:
            if hasattr(base, 'methods'):
                AbstractMethodViewType._update_from_base(
                    base, available_methods
                )
        return list(available_methods)

    @staticmethod
    def _update_from_base(
            base: type, available_methods: Set[str]
    ) -> None:
        if base.methods is not None:
            available_methods.update(method for method in base.methods)

    @staticmethod
    def _get_methods_from_namespace(namespace: dict):
        attributes = http_method_funcs
        for function_name in attributes:
            if function_name in namespace.keys():
                yield function_name.upper()


class AbstractEndpoint(View, metaclass=AbstractMethodViewType):
    """
    Defines the abstract endpoint, taking care of errors.

    Error reporting becomes a little more complicated when dealing with HTTP
    APIs, as the separation between errors and errors becomes more
    pronounced. For instance, when de-serializing invalid user input,
    the error that results from validation must be reported, but the program
    is still in a well-determined state that precludes the need for throwing
    an exception.

    Error reporting in this API relies heavily on :class:`APIException`.
    Errors can be reported either destructively by raising the
    :class:`APIException`, or non-destructively by appending the exception to
    the ``errors`` object. In order to stop execution of the endpoint and
    return an ``error`` response, raise :class:`AbstractEndpoint.Abort`.

    The ``links`` object exists primarily to display a link to the current
    endpoint. If an endpoint will be paginated, the pagination links should
    go into this object.
    """
    def __init__(
            self, session: Session, request: Request=flask_request
    ) -> None:
        """

        :param session: The database session to be used for interacting with
            the database.
        :param request: The Flask request object to use for running the request
        """
        super(AbstractEndpoint, self).__init__()
        self._session = session
        self._errors = []
        self._request = request

    def dispatch_request(self, *args, **kwargs) -> Response:
        """
        Create a session, and dispatch the request to the appropriate methods

        :param args: The function arguments built by Flask that are to be
            sent to the method called up by this dispatch
        :param kwargs: The keyword arguments built by Flask, that are going
            to be sent to the method dispatched here
        """
        if self._request.method not in self.methods:
            return self._get_method_not_allowed_response(
                self._request.method, self.methods
            )

        method = self._get_method_for_request_method(self._request.method)

        try:
            response = method(*args, **kwargs)
        except APIError as error:
            self.errors.append(error)
            response = self._error_response
        except self.Abort:
            response = self._error_response
        finally:
            self._close_session(self.database_session)

        if self.errors:
            response = self._error_response

        return response

    @property
    def request_json(self) -> dict:
        """

        :return: The JSON in the request body, if it exists
        """
        json = self._request.get_json(cache=True)
        if json is None:
            raise RequestNotJSONError()
        else:
            return json

    @property
    def links(self) -> dict:
        """

        :return: The relevant links required for the endpoint
        """
        return {'self': url_for(self.__class__.__name__, _external=True)}

    @property
    def database_session(self) -> Session:
        """

        :return: The SQLAlchemy session used to contact the database
        """
        return self._session

    @property
    def errors(self) -> List[APIError]:
        """

        :return: The errors encountered in the API
        """
        return self._errors

    @property
    def _serialized_errors(self) -> List[dict]:
        """

        :return: The errors encountered in the API after having been
            serialized
        """
        serializer = ExceptionSerializer(many=True)
        return serializer.dump(self.errors)

    @property
    def _error_status_code(self) -> int:
        """

        :return: The status code that should be thrown for an error response.
            The status code to be returned is the most general one for the
            errors provided. If all the errors have the same status code,
            then the status code to return is the status code for the
            errors. If all the errors are 400-series status codes, then the
            error code that will be returned is ``400``. If there is a
            mixture of ``400`` and ``500`` series error codes, then the
            error code to return will be ``500``
        """
        catchall_code = 500

        if self.errors:
            code = reduce(
                self._error_code_reducer,
                (error.status_code for error in self.errors)
            )
        else:
            code = catchall_code

        return code

    @property
    def _error_response(self) -> Response:
        """

        :return: A response containing the errors that were encountered
            while working with the API
        """
        response = jsonify({
            'errors': self._serialized_errors
        })
        response.status_code = self._error_status_code
        return response

    def _get_method_not_allowed_response(
            self, method: str, allowed_methods: Iterable[str]
    ) -> Response:
        """

        :param method: The method that caused the exception to be thrown
        :param allowed_methods: The allowed methods on the API
        :return: A Flask response indicating why the error was thrown
        """
        exception = MethodNotAllowedError(
            method, allowed_methods
        )
        serializer = ExceptionSerializer()

        error_schema = JSONSchema(
            title='Error Schema',
            description='Describes the schema for an API Exception'
        )

        response = jsonify({
            'errors': serializer.dump(exception),
            'meta': {
                'error_schema': error_schema.dump(serializer)
            },
            'links': self.links
        })
        response.status_code = exception.status_code
        return response

    def _close_session(self, session: Session) -> None:
        """
        Safely close the session. If there is an error from ``SQLAlchemy``,
        add it to the other errors

        :param session: The session to close
        """
        try:
            session.commit()
        except SQLAlchemyError as error:
            session.rollback()
            self.errors.append(SQLAlchemyError(error))

    @staticmethod
    def _error_code_reducer(first_code: int, second_code: int) -> int:
        """

        :param first_code: The "left side" of the status code to compare
        :param second_code: The "right side" of the status codes
        :return: The status code that should be returned
        """
        if first_code == second_code:
            return first_code
        else:
            if 400 < first_code < 500 and 400 < second_code < 500:
                return 400
            else:
                return 500

    def _get_method_for_request_method(
            self, request_method: str
    ) -> Callable[[Optional[Any]], Response]:
        """

        :param request_method: The HTTP request method requested by Flask
        :return: The method to run
        """
        desired_method = request_method.upper()
        if desired_method == "GET":
            return getattr(self, 'get')
        elif desired_method == "POST":
            return getattr(self, 'post')
        elif desired_method == "PATCH":
            return getattr(self, 'patch')
        elif desired_method == "DELETE":
            return getattr(self, 'delete')
        elif desired_method == "PUT":
            return getattr(self, 'put')
        else:
            raise ValueError("Unable to find method %s" % desired_method)

    class Abort(Exception):
        """
        Exception thrown if the endpoint has to stop. The error response
        will be returned at this point.
        """

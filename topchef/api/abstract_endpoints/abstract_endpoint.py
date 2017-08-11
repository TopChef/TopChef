"""
Provides an abstract endpoint unique to this API from which all other
endpoints will inherit. This takes care of managing the database session,
as well as providing a ``links`` object containing the endpoint to itself.
"""
from functools import reduce
from flask import Response, jsonify
from flask.views import View
from flask import url_for, Request
from flask import request as flask_request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import abc
from typing import List, Iterable, Callable, Optional, Any
from topchef.models import APIException
from topchef.models.exceptions import MethodNotAllowedException
from topchef.models.exceptions import SQLAlchemyException
from topchef.serializers import APIException as ExceptionSerializer
from topchef.serializers import JSONSchema

__all__ = ['AbstractEndpoint']


class AbstractEndpoint(View, metaclass=abc.ABCMeta):
    """
    Defines the abstract endpoint, taking care of exceptions.

    Error reporting becomes a little more complicated when dealing with HTTP
    APIs, as the separation between errors and exceptions becomes more
    pronounced. For instance, when de-serializing invalid user input,
    the error that results from validation must be reported, but the program
    is still in a well-determined state that precludes the need for throwing
    an exception.

    Error reporting in this API relies heavily on :class:`APIException`.
    Errors can be reported either destructively by raising the
    :class:`APIException`, or non-destructively by appending the exception to
    the ``errors`` object. In order to stop execution of the endpoint and
    return an ``error`` response, raise :class:`AbstractEndpoint.Abort`.
    """
    def __new__(cls, session: Session, *args, **kwargs):
        """

        :param session: The database session to use
        :return: The methods to be implemented
        """
        cls.methods = ['OPTIONS', 'HEAD']
        if hasattr(cls, 'get'):
            cls.methods.append('GET')
        if hasattr(cls, 'post'):
            cls.methods.append('POST')
        if hasattr(cls, 'put'):
            cls.methods.append('PUT')
        if hasattr(cls, 'patch'):
            cls.methods.append('PATCH')
        if hasattr(cls, 'delete'):
            cls.methods.append('DELETE')

        return super(AbstractEndpoint, cls).__new__(cls)

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
        """
        if self._request.method not in self.methods:
            return self._get_method_not_allowed_response(
                self._request.method, self.methods
            )

        method = self._get_method_for_request_method(self._request.method)

        try:
            response = method(*args, **kwargs)
        except APIException as error:
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
    def links(self):
        return {'self': url_for(self.__class__.__name__, _external=True)}

    @property
    def database_session(self) -> Session:
        return self._session

    @property
    def errors(self) -> List[APIException]:
        """

        :return: The errors encountered in the API
        """
        return self._errors

    @property
    def _serialized_errors(self) -> List[dict]:
        serializer = ExceptionSerializer(many=True)
        return serializer.dump(self.errors)

    @property
    def _error_status_code(self) -> int:
        """

        :return: The status code that should be thrown for an error response
        """
        code = reduce(
            self._error_code_reducer,
            (error.status_code for error in self.errors)
        )
        catchall_code = 500

        if code is None:
            return catchall_code
        else:
            return code

    @property
    def _error_response(self) -> Response:
        response = jsonify({'errors': self._serialized_errors})
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
        exception = MethodNotAllowedException(
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
            self.errors.append(SQLAlchemyException(error))

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
"""
Contains the exception to be thrown if a method is not allowed
"""
from topchef.models.interfaces import APIException
from typing import Iterable


class MethodNotAllowedException(APIException, Exception):
    """
    Describes an exception thrown if an HTTP method is called on an endpoint
    that does not have this method defined
    """
    def __init__(self, offending_method: str, allowed_methods: Iterable[str]):
        """

        :param offending_method: The method that resulted in the error being
            thrown
        :param allowed_methods: The allowed methods
        """
        self.offending_method = offending_method
        self.allowed_methods = allowed_methods

    @property
    def status_code(self) -> int:
        """

        :return: The standard HTTP status code for a method not being allowed
        """
        return 405

    @property
    def title(self) -> str:
        """

        :return: The exception title
        """
        return 'Method Not Implemented'

    @property
    def detail(self) -> str:
        """

        :return: A detailed message indicating why this error was thrown
        """
        return 'Attempted to call method %s. Available methods are %s' % (
            self.offending_method, ', '.join(self.allowed_methods)
        )

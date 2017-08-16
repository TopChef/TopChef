"""
Contains an error that wraps the ``ValidationError`` class from
``jsonschema``, and makes it reportable using the exception reporting
framework designed in ``AbstractEndpoint``
"""
import jsonschema
from topchef.models import APIError


class ValidationError(APIError):
    """
    Describes the error in a way that the user of the API can read
    """
    def __init__(self, validation_error: jsonschema.ValidationError):
        self._error = validation_error

    @property
    def status_code(self) -> int:
        """

        :return: The HTTP status code for this error
        """
        return 400

    @property
    def title(self) -> str:
        """

        :return: The title of the error
        """
        return 'JSONSchema Validation Error'

    @property
    def detail(self) -> str:
        """

        :return: A detailed message explaining what went wrong
        """
        return str(self._error)

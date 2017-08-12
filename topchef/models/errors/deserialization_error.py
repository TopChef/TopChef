"""
Describes a reportable exception that is thrown if Marshmallow or jsonschema
is unable to deserialize an object provided into the API. This is a
client-side error.
"""
from topchef.models import APIError


class DeserializationError(APIError):
    """
    Describes the exception
    """
    def __init__(self, validator_error_message: str) -> None:
        """

        :param validator_error_message: The error message reported by the
            validator
        """
        self._message = validator_error_message

    @property
    def status_code(self) -> int:
        """

        :return: Since this error is thrown when the user inputs invalid
            data, the status code for this error is ``400 BAD REQUEST``
        """
        return 400

    @property
    def detail(self) -> str:
        """

        :return: The error message reported by the serializer
        """
        return self._message

    @property
    def title(self):
        """

        :return: The title of the error
        """
        return 'Deserialization Error From Client Data'

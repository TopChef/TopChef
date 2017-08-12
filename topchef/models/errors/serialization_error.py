"""
Describes an error to be thrown if the server is provided with some invalid
data from the API
"""
from topchef.models import APIError


class SerializationError(APIError):
    """
    Describes an error thrown if the server receives an object that it
    cannot serialize with a particular serializer. This is a ``500`` series
    error. If this error is encountered in production, the API maintainer
    should hang their head in shame.
    """
    def __init__(self, marshmallow_error: str) -> None:
        """

        :param marshmallow_error: The error message thrown by marshmallow
        """
        self._error = marshmallow_error

    @property
    def status_code(self) -> int:
        """

        :return: The status code for this error
        """
        return 500

    @property
    def title(self) -> str:
        """

        :return: The title of this exception
        """
        return 'Serialization Error From Server Data'

    @property
    def detail(self) -> str:
        """

        :return: A detailed error message
        """
        return 'The serializer used by this server threw error "%s". Report ' \
               'this to the maintainer as soon as possible.'

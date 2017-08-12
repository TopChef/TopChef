"""
Contains an exception thrown if a service is not found
"""
import abc
from uuid import UUID
from topchef.models.interfaces import APIError


class ServiceNotFoundError(APIError, metaclass=abc.ABCMeta):
    """
    Thrown if a service with a particular ID is not found
    """
    @property
    def title(self) -> str:
        """

        :return: The title of the exception
        """
        return 'Service Not Found'

    @property
    def status_code(self) -> int:
        """

        :return: The HTTP status code that should be thrown if a service is
            not found
        """
        return 404

    @property
    @abc.abstractmethod
    def detail(self) -> str:
        """

        :return: A detailed error message explaining why this error was
            thrown
        """
        raise NotImplementedError()


class ServiceWithUUIDNotFound(ServiceNotFoundError):
    """
    Thrown if a service with a particular UUID is not found
    """
    def __init__(self, offending_uuid: UUID, *args) -> None:
        super(ServiceWithUUIDNotFound, self).__init__(*args)
        self.bad_uuid = offending_uuid

    @property
    def detail(self) -> str:
        """

        :return: A detailed error message explaining why this error was thrown
        """
        return 'A service with UUID %s does not exist' % str(self.bad_uuid)
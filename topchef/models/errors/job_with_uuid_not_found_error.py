"""
Contains an exception thrown if a job with a particular ID is not found
"""
from ..interfaces import APIError
from uuid import UUID


class JobWithUUIDNotFound(APIError):
    """
    Thrown if a job with a given UUID is not found
    """
    def __init__(self, offending_id: UUID):
        self._job_id = offending_id

    @property
    def status_code(self) -> int:
        """

        :return: The 404 status code indicating that a resource was not found
        """
        return 404

    @property
    def title(self) -> str:
        """

        :return: The title of the error
        """
        return 'Job Not Found'

    @property
    def detail(self) -> str:
        """

        :return: A detailed message explaining what went wrong
        """
        return 'A job with id %s was not found' % self._job_id
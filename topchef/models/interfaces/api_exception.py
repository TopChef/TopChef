"""
Describes the interface for a reportable exception that can occur in the API
at some point.
"""
import abc


class APIException(Exception, metaclass=abc.ABCMeta):
    """
    Describes the interface for working with an API Exception.
    """
    @property
    def status_code(self) -> int:
        """

        :return: The status code that should ideally be associated with this
            exception. For instance, if a service is not found, the status code
            for the error is a ``404``. If multiple exceptions are thrown of
            a particular exception series, then the most general status code
            will be returned. For instance, if two errors are ``404`` and
            ``403``, then the error returned will be ``400``. If both
            client-side (``4xx``) and server-side (``5xx``) errors are
            encountered, the server will return ``500``.
        """
        raise NotImplementedError()

    @property
    def title(self) -> str:
        """

        :return: The title associated with this exception. This should be
        common across exceptions of a particular type
        """
        raise NotImplementedError()

    @property
    def detail(self) -> str:
        """

        :return: A detailed message associated with the exception
        """
        raise NotImplementedError()

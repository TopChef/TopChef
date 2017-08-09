"""
Describes an interface for a resource capable of retrieving metadata for the
API
"""
import abc


class APIMetadata(object, metaclass=abc.ABCMeta):
    """
    Describes the metadata for the API
    """
    @property
    @abc.abstractmethod
    def maintainer_email(self) -> str:
        """

        :return: An email address for the API maintainer. Users should be
        able to send emails to this address to inform the maintainer of any
        bugs in the API.
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def maintainer_name(self) -> str:
        """

        :return: The name of the API's maintainer
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def source_code_repository_url(self) -> str:
        """

        :return: A URL to the repository where the API source code is
        located. Users should be able to use resources at this URL in order
        to inspect the source code
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """

        :return: The version of the API being deployed
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def documentation_url(self) -> str:
        """

        :return: A URL to the API's documentation. This includes both user
        documentation such as tutorials, and reference documentation for
        things like Python API methods
        """
        raise NotImplementedError()

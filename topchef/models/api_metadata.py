"""
Provides a model that pulls the application metadata from The ``CONFIG``
object defined in :mod:`topchef.config`.
"""
from topchef.config import config, Config
from topchef.models.interfaces.api_metadata import APIMetadata as IAPIMetadata

__all__ = ["APIMetadata"]


class APIMetadata(IAPIMetadata):
    """
    Model responsible for pulling metadata from the config file
    """
    def __init__(self, app_configuration: Config=config) -> None:
        """

        :param app_configuration: The configuration object from which
            metadata is to be pulled. By default, this is the ``config``
            object from :mod:`topchef.config`.
        """
        super(APIMetadata, self).__init__()
        self._config = app_configuration

    @property
    def maintainer_email(self) -> str:
        """

        :return: The email-address of the maintainer of this API
        """
        return config.AUTHOR_EMAIL

    @property
    def maintainer_name(self) -> str:
        """

        :return: A name that can be used to look up the human responsible
            for maintaining this API
        """
        return config.AUTHOR

    @property
    def source_code_repository_url(self) -> str:
        """

        :return: The URL to the repository where the source code for the API
            is hosted
        """
        return config.SOURCE_REPOSITORY

    @property
    def version(self) -> str:
        """

        :return: The version of the API
        """
        return config.VERSION

    @property
    def documentation_url(self) -> str:
        """

        :return: A URL where documentation for the API can be obtained. This
            documentation MUST contain a description of the available API
            endpoints, the methods that can be performed on them, and what
            errors may arise from using the API
        """
        return config.DOCUMENTATION_URL

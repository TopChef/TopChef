"""
Contains a generator for :class:`topchef.models.APIMetadata`
"""
from hypothesis.strategies import composite, text
from topchef.models import APIMetadata as APIMetadataInterface


class _APIMetadata(APIMetadataInterface):
    """
    A container for API metadata that stores the required metadata
    """
    def __init__(self, maintainer_name: str, version: str):
        self._maintainer_name = maintainer_name
        self._version = version

    @property
    def maintainer_email(self) -> str:
        return 'email@example.com'

    @property
    def maintainer_name(self) -> str:
        return self._maintainer_name

    @property
    def source_code_repository_url(self) -> str:
        return 'http://repository.url'

    @property
    def documentation_url(self) -> str:
        return 'http://documentation.url'

    @property
    def version(self) -> str:
        return self._version


@composite
def api_metadata(
        draw, maintainer_names=text(), versions=text()
) -> APIMetadataInterface:
    """

    :param draw: A function supplied by the ``@composite`` decorator,
        which knows how to draw a randomly-generated sample from the
        strategies provided by ``hypothesis``
    :param maintainer_names: A generator for maintainer names
    :param versions: A generator for API versions
    :return: A randomly-generated API Metadata model
    """
    return _APIMetadata(
        draw(maintainer_names), draw(versions)
    )

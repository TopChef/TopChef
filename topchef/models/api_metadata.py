from .abstract_api_metadata import AbstractAPIMetadata
from topchef.config import config


class APIMetadata(AbstractAPIMetadata):
    @property
    def maintainer_email(self) -> str:
        return config.AUTHOR_EMAIL

    @property
    def maintainer_name(self) -> str:
        return config.AUTHOR

    @property
    def source_code_repository_url(self) -> str:
        return config.SOURCE_REPOSITORY

    @property
    def version(self) -> str:
        return config.VERSION

    @property
    def documentation_url(self) -> str:
        return config.DOCUMENTATION_URL

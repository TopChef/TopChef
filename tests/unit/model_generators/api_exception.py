"""
Contains a generator for APIExceptions
"""
from topchef.models import APIException as APIExceptionInterface
from hypothesis.strategies import composite, integers, text

__all__ = ['api_exceptions']


class _APIException(APIExceptionInterface):
    """
    A local store of randomly-generated data for testing
    """
    def __init__(self, status_code: int, title: str, detail: str) -> None:
        """

        :param status_code: The status code for the mock exception
        :param title: The title for the exception
        :param detail: A detailed message explaining what went wrong
        """
        self._status_code = status_code
        self._title = title
        self._detail = detail

    @property
    def status_code(self) -> int:
        """

        :return: The status code
        """
        return self._status_code

    @property
    def title(self) -> str:
        """

        :return: The title
        """
        return self._title

    @property
    def detail(self) -> str:
        """

        :return: The detailed message
        """
        return self._detail


@composite
def api_exceptions(
        draw,
        status_codes=integers(min_value=400, max_value=599),
        titles=text(),
        details=text()
) -> APIExceptionInterface:
    return _APIException(
        draw(status_codes), draw(titles), draw(details)
    )

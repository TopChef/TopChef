"""
Contains an exception to be thrown if the SQL library acts up
"""
from topchef.models.interfaces import APIError
from sqlalchemy.exc import SQLAlchemyError


class SQLAlchemyError(APIError, Exception):
    """
    Base class for an HTTP exception thrown as a result of a SQLAlchemy error
    """
    def __init__(self, underlying_exception: SQLAlchemyError):
        self.exception = underlying_exception

    @property
    def status_code(self) -> int:
        """

        :return:
        """
        return 503

    @property
    def title(self) -> str:
        """

        :return: The title of the error
        """
        return "Database Error"

    @property
    def detail(self) -> str:
        """

        :return: A message indicating why the API failed
        """
        return 'SQLAlchemy threw error %s' % str(self.exception)

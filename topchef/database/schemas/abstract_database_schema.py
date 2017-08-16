"""
Describes the database schemas
"""
import abc
from sqlalchemy import Table, MetaData


class AbstractDatabaseSchema(object, metaclass=abc.ABCMeta):
    """
    Defines the interface for the database schema
    """

    @property
    @abc.abstractmethod
    def services(self) -> Table:
        """

        :return: The table used to write information about services
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def jobs(self) -> Table:
        """

        :return: The table used to write information about jobs
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def job_sets(self) -> Table:
        """

        :return: The table associated with job sets
        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def metadata(self) -> MetaData:
        """

        :return: The metadata container used by SQLAlchemy to store metadata
         related to the DB schema
        """
        raise NotImplementedError()

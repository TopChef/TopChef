"""
Contains the interface for interacting with a ``SQLAlchemy`` database
schema. Each table in the schema should map to a property defined in this
interface. This is done to prevent accidental overwriting of tables. The
``metadata`` property in this schema holds the instance of
:class:`sqlalchemy.MetaData`
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

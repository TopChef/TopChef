import abc
from ..schemas import database
from sqlalchemy.ext.declarative import declarative_base
from typing import Generic, TypeVar

BASE = declarative_base(metadata=database.metadata)
T = TypeVar('T')


class AbstractDatabaseModel(Generic[T]):

    @classmethod
    @abc.abstractclassmethod
    def new(cls, *args, **kwargs) -> T:
        """
        Create a new instance of the database model

        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

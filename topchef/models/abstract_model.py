import abc
from uuid import UUID
from typing import TypeVar
from sqlalchemy.orm import Session
from topchef.storage import AbstractStorage


class AbstractModel(object, metaclass=abc.ABCMeta):
    """
    Base class for a model class that can be written to multiple storage
    media. This class is capable of checking its own consistency
    """
    T = TypeVar()

    @abc.abstractmethod
    def write(self):
        """

        Write this object to persistent storage, taking ALL storage media
        from one consistent state to another
        """
        raise NotImplementedError()

    @abc.abstractmethod
    @property
    def is_consistent(self):
        """

        :return: True if the model class is consistent.
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def from_storage(
            cls,
            service_id: UUID,
            db_session: Session,
            storage: AbstractStorage
    ) -> T:
        """

        :return: The class, built from the required storage media
        """
        raise NotImplementedError()

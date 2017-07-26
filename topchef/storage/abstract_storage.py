"""
Describes an abstract document store
"""
import abc
from uuid import UUID
from collections.abc import MutableMapping
from typing import Iterator, Dict, Optional, Any


class DocumentStorage(MutableMapping, metaclass=abc.ABCMeta):
    """
    Defines the interface for a document store
    """
    @abc.abstractmethod
    def __getitem__(self, model_id: UUID) -> Dict[str, Optional[Any]]:
        """

        :param model_id:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __setitem__(
            self,
            model_id: UUID,
            new_json: Dict[str, Optional[Any]]
    ) -> None:
        """

        :param model_id:
        :param new_json:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __delitem__(self, model_id: UUID) -> None:
        """

        :param model_id:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def __iter__(self) -> Iterator[UUID]:
        """

        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def add(self, element: Dict[str, Optional[Any]]) -> UUID:
        raise NotImplementedError()

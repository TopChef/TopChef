"""
Base class for storing documents in a relational DB
"""
from .abstract_storage import DocumentStorage
from uuid import UUID
from typing import Dict, Optional, Any, Iterable
from sqlalchemy.orm import sessionmaker, Session
from .json_document_model import JSONDocument


class RelationalDatabaseStorage(DocumentStorage):
    """
    Stores documents in a table in a relational DB. I'm so sorry Ted Codd.
    """
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def __getitem__(self, document_id: UUID) -> Dict[str, Optional[Any]]:
        """

        :param document_id: The ID of the document to retrieve
        :return: The document with the desired ID
        """
        session = self._session_factory()  # type: Session
        document_from_storage = self._get_document_from_storage(
            session, document_id
        )

        return document_from_storage.document

    def __setitem__(
            self,
            model_id: UUID,
            new_json: Dict[str, Optional[Any]]
    ) -> None:
        """

        :param model_id: The ID of the document to set
        :param new_json: The new JSON to be set
        """
        session = self._session_factory()  # type: Session
        document = self._get_document_from_storage(session, model_id)

        document.document = new_json
        session.add(document)
        self._safely_commit_session(session)

    def __delitem__(self, model_id: UUID) -> None:
        """

        :param model_id: The ID of the document to delete
        """
        session = self._session_factory()  # type: Session
        document = self._get_document_from_storage(session, model_id)
        session.delete(document)
        self._safely_commit_session(session)

    def __iter__(self) -> Iterable[UUID]:
        """

        :return: All the document IDs available
        """
        session = self._session_factory()  # type: Session
        return session.query(JSONDocument.id).all()

    def __len__(self) -> int:
        """

        :return: The number of documents stored in this storage
        """
        session = self._session_factory()  # type: Session
        return session.query(JSONDocument).count()

    def add(self, element: Dict[str, Optional[Any]]) -> UUID:
        session = self._session_factory()
        document = JSONDocument(element)
        session.add(document)
        self._safely_commit_session(session)

        return document.id

    @staticmethod
    def _get_document_from_storage(
            session: Session, model_id: UUID
    ) -> JSONDocument:
        """

        :param session: The SQLAlchemy session to use for getting the document
        :param model_id: The ID of the document to retrieve
        :return: The model class containing the document
        """
        document = session.query(JSONDocument).filter_by(
            id=model_id
        ).first()  # type: JSONDocument

        if document is None:
            raise KeyError('A document with ID %s does not exist' % model_id)

        return document

    @staticmethod
    def _safely_commit_session(session: Session) -> None:
        """

        :param session: The session to close
        """
        try:
            session.commit()
        except:
            session.rollback()
            raise

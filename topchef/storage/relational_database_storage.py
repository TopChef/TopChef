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
        :return:
        """
        session = self._session_factory()  # type: Session

        return self._get_document_from_storage(session, document_id).document

    def __setitem__(
            self,
            model_id: UUID,
            new_json: Dict[str, Optional[Any]]
    ) -> None:
        """

        :param model_id:
        :param new_json:
        """
        session = self._session_factory()  # type: Session

        document = session.query(JSONDocument).filter_by(
            document_id=model_id).first()  # type: Optional[JSONDocument]

        if document is None:
            raise KeyError('The document %s does not exist' % str(model_id))

        document.document = new_json
        session.add(document)
        self._safely_commit_session(session)

    def __delitem__(self, model_id: UUID) -> None:
        """

        :param model_id:
        :return:
        """
        session = self._session_factory()  # type: Session
        document = self._get_document_from_storage(session, model_id)
        session.delete(document)
        self._safely_commit_session(session)

    def __iter__(self) -> Iterable:
        session = self._session_factory()  # type: Session
        return session.query(JSONDocument.id).all()

    def __len__(self) -> int:
        session = self._session_factory()  # type: Session
        return session.query(JSONDocument).count()

    @staticmethod
    def _get_document_from_storage(
            session: Session, model_id: UUID
    ) -> JSONDocument:
        document = session.query(JSONDocument).filter_by(
            id=model_id
        ).first()  # type: JSONDocument
        return document

    @staticmethod
    def _safely_commit_session(session: Session) -> None:
        try:
            session.commit()
        except:
            session.rollback()
            raise

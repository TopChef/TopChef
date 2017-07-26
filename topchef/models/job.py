from uuid import UUID
from collections import namedtuple
from sqlalchemy.orm import Session
from .abstract_model import AbstractModel
from ..database import Job as DatabaseJob
from ..storage import DocumentStorage
from typing import Optional, Any, Dict
from .service import Service
from ..database.schemas.job_status import JobStatus


class Job(AbstractModel):
    """
    Base class for a TopChef job
    """
    T = 'Job'
    D = DatabaseJob

    Documents = namedtuple('_Documents', [
        'parameters', 'result'
    ])

    def __init__(
            self,
            service: Service,
            job_id: UUID,
            parameters: dict,
            status: JobStatus=JobStatus.REGISTERED,
            results: Dict[str, Optional[Any]]=None
    ) -> None:
        """

        :param job_id:
        :param parameters:
        :param results:
        """
        self.service = service
        self.id = job_id
        self.parameters = parameters
        self.status = status
        self.results = results

    @classmethod
    def _get_database_model(
            cls, model_id: UUID, db_session: Session
    ) -> Optional[D]:
        return db_session.query(
            DatabaseJob
        ).filter_by(id=model_id).first()

    @classmethod
    def _get_documents_for_database_model(
            cls, model: D, storage: DocumentStorage
    ) -> 'Job.Documents':
        return cls.Documents(
            storage[model.parameters_id], storage[model.results_id]
        )

    def _write_new_model(self, session: Session, storage: DocumentStorage):
        parameter_id = storage.add(self.parameters)
        results_id = storage.add(self.results)

        db_job = DatabaseJob(
            self.id, self.status, parameter_id, self.service,
            results_id
        )

        session.add(db_job)

        try:
            session.commit()
        except:
            session.rollback()
            del storage[parameter_id]
            del storage[results_id]
            raise

    @classmethod
    def from_storage(
            cls,
            model_id: UUID,
            db_session: Session,
            storage: DocumentStorage
    ) -> 'Job':
        db_model = cls._get_database_model(model_id, db_session)
        documents = cls._get_documents_for_database_model(db_model, storage)

        return cls(
            db_model.service, db_model.id, documents.parameters,
            documents.result
        )

    def write(self, session: Session, storage: DocumentStorage) -> None:
        db_model = self._get_database_model(self.id, session)

        if db_model is None:
            self._write_new_model(session, storage)

        storage[db_model.parameters_id] = self.parameters
        storage[db_model.results_id] = self.results
        session.add(db_model)
        session.commit()

    def delete(self, session: Session, storage: DocumentStorage):
        db_model = self._get_database_model(self.id, session)

        del storage[db_model.parameters_id]
        del storage[db_model.results_id]

        session.delete(db_model)
        session.commit()

    def __eq__(self, other: T) -> bool:
        return self.id == other.id

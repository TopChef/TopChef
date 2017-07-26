"""
Describes a top-level service
"""
from uuid import UUID
from collections import namedtuple
from .abstract_model import AbstractModel
from ..database import Service as DatabaseService
from ..storage import DocumentStorage
from sqlalchemy.orm import Session


class Service(AbstractModel):
    """
    Base class for a TopChef service
    """
    T = 'Service'
    D = DatabaseService

    Documents = namedtuple(
        '_Documents', ['job_registration_schema',
                       'job_result_schema'])

    def __init__(self, service_id: UUID, name: str, description: str,
                 job_registration_schema: dict, job_result_schema: dict):
        self.id = service_id
        self.name = name
        self.description = description
        self.job_registration_schema = job_registration_schema
        self.job_result_schema = job_result_schema

    @classmethod
    def get_database_model(cls, model_id: UUID, db_session: Session) -> D:
        return db_session.query(
            DatabaseService
        ).filter_by(id=model_id).first()

    @classmethod
    def get_documents_for_database_model(
            cls, model: D, storage: DocumentStorage
    ) -> 'Service.Documents':
        return cls.Documents(
            storage[model.job_registration_schema_reference],
            storage[model.job_result_schema_reference]
        )

    @classmethod
    def from_storage(
            cls, model_id: UUID, db_session: Session, storage: DocumentStorage
    ) -> 'Service':
        db_model = cls.get_database_model(model_id, db_session)

        if db_model is None:
            raise ValueError('A model with id %s does not exist', model_id)

        documents = cls.get_documents_for_database_model(db_model, storage)

        return cls(
            model_id, db_model.name, db_model.description,
            documents.job_registration_schema,
            documents.job_result_schema
        )

    def write(self, session: Session, storage: DocumentStorage):
        db_model = self.get_database_model(self.id, session)

        if db_model is None:
            self._write_new_model(session, storage)
        else:
            storage[db_model.job_registration_schema_reference] = \
                self.job_registration_schema
            storage[db_model.job_result_schema_reference] = self.job_result_schema
            session.add(db_model)
            session.commit()

    def delete(self, session: Session, storage: DocumentStorage) -> None:
        db_model = self.get_database_model(
            self.id, session
        )
        session.delete(db_model)
        del storage[db_model.job_registration_schema_reference]
        del storage[db_model.job_result_schema_reference]
        session.commit()

    def _write_new_model(self, session: Session, storage: DocumentStorage):
        registration_schema_id = storage.add(self.job_registration_schema)
        result_schema_id = storage.add(self.job_result_schema)

        db_service = DatabaseService(
            self.id,
            self.name, self.description, registration_schema_id,
            result_schema_id
        )

        session.add(db_service)

        try:
            session.commit()
        except:
            session.rollback()
            del storage[registration_schema_id]
            del storage[result_schema_id]
            raise

    def __eq__(self, other: T) -> bool:
        return self.id == other.id

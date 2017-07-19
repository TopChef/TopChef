"""
Describes a top-level service
"""
from .abstract_model import AbstractModel
from uuid import UUID
from topchef.storage import AbstractStorage
from topchef.database import Service as DatabaseService
from sqlalchemy.orm import Session


class Service(AbstractModel):
    """
    Base class for a TopChef service
    """
    T = 'Service'

    def __init__(self, id: UUID, name: str, description: str,
                 job_registration_schema: dict, job_result_schema: dict):
        self.id = id
        self.name = name
        self.description = description
        self.job_registration_schema = job_registration_schema
        self.job_result_schema = job_result_schema

    @classmethod
    def from_storage(
            cls, service_id: UUID, database_session: Session,
            storage: AbstractStorage
    ) -> T:
        """

        :param service_id:
        :param database_session:
        :param storage:
        :return:
        """
        db_service = database_session.query(DatabaseService).filter_by(
            id=service_id
        ).first()  # type: DatabaseService
        name = db_service.name
        description = db_service.description

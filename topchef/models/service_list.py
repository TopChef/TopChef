from .abstract_service_list import AbstractServiceList
from uuid import UUID
from sqlalchemy.orm import Session
from topchef.database.models import Service as DatabaseService
from topchef.models.service import Service
from typing import Union
from topchef.json_type import JSON_TYPE as JSON


class ServiceList(AbstractServiceList):
    """
    Implements a means of getting services from a relational DB back end
    """
    def __init__(self, session: Session) -> None:
        """

        :param session: The database session to use for getting services
        """
        self.session = session

    def __getitem__(self, service_id: UUID) -> Service:
        db_model = self._get_db_model_by_id(self.session, service_id)
        return Service(db_model)

    def __setitem__(self, service_id: UUID, service: Service) -> None:
        db_model = self._get_db_model_by_id(self.session, service_id)

        db_model.is_service_available = service.is_service_available
        db_model.name = service.name
        db_model.description = service.description

        self.session.add(db_model)

    def __delitem__(self, service_id: UUID) -> None:
        db_model = self._get_db_model_by_id(self.session, service_id)

        for job in db_model.jobs:
            self.session.delete(job)
        self.session.delete(db_model)

    def __contains__(
            self, service_or_service_id: Union[UUID, Service]
    ) -> bool:
        if isinstance(service_or_service_id, Service):
            is_in_collection = self._check_service_membership(
                service_or_service_id
            )
        else:
            is_in_collection = self._check_id_membership(
                service_or_service_id
            )
        return is_in_collection

    def __len__(self) -> int:
        return self.session.query(DatabaseService).count()

    def __iter__(self):
        services = self.session.query(DatabaseService).all()

        for service in services:
            yield Service(service)

    async def __aiter__(self):
        services = self.session.query(DatabaseService).all()

        for service in services:
            yield Service(service)

    def new(
            self, name: str, description: str, registration_schema: JSON,
            result_schema: JSON) -> Service:
        service = DatabaseService.new(
            name, description, registration_schema, result_schema
        )
        self.session.add(service)
        return Service(service)

    @staticmethod
    def _get_db_model_by_id(
            session: Session, service_id: UUID
    ) -> DatabaseService:

        db_model = session.query(
            DatabaseService
        ).filter_by(
            id=service_id
        ).first()

        if db_model is None:
            raise KeyError('A model with that ID does not exist')

        return db_model

    def _check_service_membership(self, service: Service):
        number_of_matches = self.session.query(DatabaseService).filter_by(
            id=service.id).count()
        return bool(number_of_matches)

    def _check_id_membership(self, service_id: UUID) -> bool:
        number_of_matches = self.session.query(DatabaseService).filter_by(
            id=service_id
        ).count()
        return bool(number_of_matches)

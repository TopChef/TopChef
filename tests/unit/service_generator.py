from uuid import UUID
from unittest.mock import MagicMock
from hypothesis.strategies import text, booleans, uuids, composite
from topchef.models import Service as IService
from topchef.models.service import Service as DatabaseService
from topchef.models import Job
from topchef.database.models.job import Job as DatabaseJob
from topchef.json_type import JSON_TYPE as JSON
from sqlalchemy.orm import Session
from typing import Callable


class Service(IService):
    """
    A custom-generated service
    """
    new_service_creator = MagicMock()
    new_job_creator = MagicMock()
    jobs_list = MagicMock()

    def __init__(
            self, service_id: UUID, name: str, desc: str, is_available: bool
    ) -> None:
        self._id = service_id
        self._name = name
        self._description = desc
        self._is_available = is_available

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        """

        :return:
        """
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        self._description = new_description

    @property
    def job_registration_schema(self) -> JSON:
        return {'type': 'object'}

    @property
    def job_result_schema(self) -> JSON:
        return {'type': 'object'}

    @property
    def is_service_available(self) -> bool:
        return self._is_available

    @is_service_available.setter
    def is_service_available(self, service_available: bool) -> None:
        self._is_available = service_available

    @classmethod
    def new(
            cls,
            name: str,
            description: str,
            registration_schema: JSON,
            result_schema: JSON,
            database_session: Session
    ) -> IService:
        return cls.new_service_creator(
            name, description, registration_schema, result_schema,
            database_session
        )

    def new_job(
            self,
            parameters: JSON,
            database_job_constructor: Callable[
                [DatabaseService, JSON], Job]=DatabaseJob.new
    ):
        return self.new_job_creator(
            parameters, database_job_constructor=database_job_constructor
        )

    @property
    def jobs(self):
        return self.jobs_list


@composite
def services(
        draw,
        service_id=uuids(), name=text(), description=text(),
        is_available=booleans()
) -> IService:
    return Service(
        draw(service_id), draw(name), draw(description), draw(is_available)
    )

from ..database.models import Job as DatabaseJob
from ..database.models import JobStatus
from .abstract_job import AbstractJob
from uuid import UUID
from ..json_type import JSON_TYPE as JSON
import json
from typing import Optional
from datetime import datetime


class Job(AbstractJob):
    def __init__(self, database_job: DatabaseJob):
        self.db_model = database_job

    @property
    def id(self) -> UUID:
        return self.db_model.id

    @property
    def status(self) -> JobStatus:
        return self.db_model.status

    @status.setter
    def status(self, new_status: JobStatus) -> None:
        self.db_model.status = new_status

    @property
    def parameters(self) -> JSON:
        return self.db_model.parameters

    @property
    def results(self) -> Optional[JSON]:
        return self.db_model.results

    @property
    def date_submitted(self) -> datetime:
        return self.db_model.date_submitted

    @results.setter
    def results(self, new_results: JSON) -> None:
        self._assert_json(new_results)
        self.db_model.results = new_results

    @staticmethod
    def _assert_json(json_to_set):
        try:
            json.loads(json.dumps(json_to_set))
        except json.JSONDecodeError as error:
            raise ValueError(
                'The input is not JSON', error
            )

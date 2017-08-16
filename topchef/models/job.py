"""
Implements a job that maps to the 
"""
import json
from datetime import datetime
from typing import Optional
from uuid import UUID
from topchef.models.interfaces.job import Job as JobInterface
from ..database.models import Job as DatabaseJob
from ..database.models import JobStatus as DatabaseJobStatus
from ..json_type import JSON_TYPE as JSON


class Job(JobInterface):
    """
    Contains an implementation of the job interface
    """
    _DATABASE_JOB_STATUS_LOOKUP = {
        DatabaseJobStatus.REGISTERED: JobInterface.JobStatus.REGISTERED,
        DatabaseJobStatus.COMPLETED: JobInterface.JobStatus.COMPLETED,
        DatabaseJobStatus.WORKING: JobInterface.JobStatus.WORKING,
        DatabaseJobStatus.ERROR: JobInterface.JobStatus.ERROR
    }

    _MODEL_JOB_STATUS_LOOKUP = {
        JobInterface.JobStatus.REGISTERED: DatabaseJobStatus.REGISTERED,
        JobInterface.JobStatus.COMPLETED: DatabaseJobStatus.COMPLETED,
        JobInterface.JobStatus.WORKING: DatabaseJobStatus.WORKING,
        JobInterface.JobStatus.ERROR: DatabaseJobStatus.ERROR
    }

    def __init__(self, database_job: DatabaseJob):
        """

        :param database_job: The database model for the job
        """
        self.db_model = database_job

    @property
    def id(self) -> UUID:
        """

        :return: The job ID
        """
        return self.db_model.id

    @property
    def status(self) -> JobInterface.JobStatus:
        return self._DATABASE_JOB_STATUS_LOOKUP[self.db_model.status]

    @status.setter
    def status(self, new_status: JobInterface.JobStatus) -> None:
        self.db_model.status = self._MODEL_JOB_STATUS_LOOKUP[new_status]

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

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.id))

    @staticmethod
    def _assert_json(json_to_set):
        try:
            json.loads(json.dumps(json_to_set))
        except json.JSONDecodeError as error:
            raise ValueError(
                'The input is not JSON', error
            )

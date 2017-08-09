"""
Contains a generator for creating jobs
"""
from uuid import UUID
from datetime import datetime
from hypothesis.strategies import composite, uuids, text, sampled_from
from hypothesis.strategies import dictionaries, datetimes
from topchef.models import Job as JobInterface


class _Job(JobInterface):
    """
    Provides an implementation of the ``JobInterface`` that works with
    randomly-generated data
    """
    def __init__(
            self,
            job_id: UUID,
            status: JobInterface.JobStatus,
            parameters: dict,
            results: dict,
            date_submitted: datetime
    ):
        self._job_id = job_id
        self._status = status
        self._parameters = parameters
        self._results = results
        self._date_submitted = date_submitted

    @property
    def id(self) -> UUID:
        return self._job_id

    @property
    def status(self) -> JobInterface.JobStatus:
        return self._status

    @status.setter
    def status(self, new_status: JobInterface.JobStatus) -> None:
        self._status = new_status

    @property
    def parameters(self) -> dict:
        return self._parameters

    @property
    def results(self) -> dict:
        return self._results

    @results.setter
    def results(self, new_results: dict) -> None:
        self._results = new_results

    @property
    def date_submitted(self) -> datetime:
        return self._date_submitted


@composite
def jobs(
        draw,
        ids=uuids(),
        statuses=sampled_from(JobInterface.JobStatus),
        parameters=dictionaries(text(), text()),
        results=dictionaries(text(), text()),
        dates_submitted=datetimes()
) -> JobInterface:
    return _Job(
        draw(ids), draw(statuses), draw(parameters), draw(results),
        draw(dates_submitted)
    )


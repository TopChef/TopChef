"""
Contains a generator for creating jobs
"""
from uuid import UUID
from datetime import datetime
from hypothesis.strategies import composite, uuids, text, sampled_from
from hypothesis.strategies import dictionaries, datetimes
from topchef.models import Job as JobInterface


class Job(JobInterface):
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
            date_submitted: datetime,
            parameter_schema: dict,
            result_schema: dict
    ) -> None:
        """

        :param job_id: The Job ID that this job will have.
        :param status: The job status
        :param parameters: The parameters with which this job was created
        :param results: The job results
        :param date_submitted: The date that this job was completed on
        :param parameter_schema: The schema that is to be satisified in
            order to successfully create parameters for a job
        :param result_schema: The schema that must be satisified in order to
            post job results.
        """
        self._job_id = job_id
        self._status = status
        self._parameters = parameters
        self._results = results
        self._date_submitted = date_submitted
        self._parameter_schema = parameter_schema
        self._result_schema = result_schema

    @property
    def id(self) -> UUID:
        """

        :return: The job ID
        """
        return self._job_id

    @property
    def status(self) -> JobInterface.JobStatus:
        """

        :return: The current job status
        """
        return self._status

    @status.setter
    def status(self, new_status: JobInterface.JobStatus) -> None:
        """

        :param new_status: The desired job status to set
        """
        self._status = new_status

    @property
    def parameters(self) -> dict:
        """

        :return: The parameters that have been set with this job
        """
        return self._parameters

    @property
    def results(self) -> dict:
        """

        :return: The results that have been set
        """
        return self._results

    @results.setter
    def results(self, new_results: dict) -> None:
        """

        :param new_results: The new results to set. This is meant to
            simulate the behaviour that occurs when a job is finished and
            the results are modified
        """
        self._results = new_results

    @property
    def date_submitted(self) -> datetime:
        """

        :return: A randomly-generated date that represents when the
            simulated job was completed
        """
        return self._date_submitted

    @property
    def parameter_schema(self) -> dict:
        """

        :return: A randomly-generated dictionary representing the schema for
            the parameters
        """
        return self._parameter_schema

    @property
    def result_schema(self) -> dict:
        """

        :return: A randomly-generated dictionary representing the schema
            that must be satisfied in order to post results to the job
        """
        return self._result_schema

    def __hash__(self) -> int:
        """

        :return: A hash calculation that lets one express a job uniquely,
            and use it in hashmap-based types like dictionary keys or sets
        """
        return hash((self.__class__.__name__, self.id))

    def __repr__(self) -> str:
        """

        :return: The code used to create this instance
        """
        return '%s(job_id=%s, status=%s, parameters=%s, results=%s, ' \
            'date_submitted=%s' % (
                self.__class__.__name__,
                self._job_id,
                self._status,
                self._parameters,
                self._results,
                self._date_submitted
            )


@composite
def jobs(
        draw,
        ids=uuids(),
        statuses=sampled_from(JobInterface.JobStatus),
        parameters=dictionaries(text(), text()),
        results=dictionaries(text(), text()),
        dates_submitted=datetimes(),
        registration_schemas=dictionaries(text(), text()),
        result_schemas=dictionaries(text(), text())
) -> JobInterface:
    """

    :param draw: A function that can take a strategy and draw a datum from it
    :param ids: A hypothesis strategy (statisticians should read "random
        variable"), that represents the set of all valid job IDs
    :param statuses: A hypothesis strategy that samples from the set of all
        allowed job statuses
    :param parameters: A hypothesis strategy that samples from all job
        parameters
    :param results: A hypothesis strategy that represents the possible results
    :param dates_submitted: A hypothesis strategy that represents the
        possible dates that can be submitted
    :param registration_schemas: The possible job registration schemas
    :param result_schemas: The possible job result schemas
    :return: A randomly-generated implementation of :class:`JobInterface`
    """
    return Job(
        draw(ids), draw(statuses), draw(parameters), draw(results),
        draw(dates_submitted),
        draw(registration_schemas),
        draw(result_schemas)
    )

from .abstract_database_schema import AbstractDatabaseSchema
from .job_status import JobStatus
from datetime import datetime
from sqlalchemy import Table, Column, MetaData, String, Boolean, Integer
from sqlalchemy import DateTime, ForeignKey, Enum
from ..uuid_database_type import UUID
from ..json_type import JSON


class DatabaseSchema(AbstractDatabaseSchema):
    """
    Describes the schema for the database
    """
    _GENERAL_JSON_SCHEMA = {'type': 'object'}

    _metadata = MetaData()
    _services = Table(
        'services', _metadata,
        Column('service_id', UUID, primary_key=True, nullable=False),
        Column('name', String(30), nullable=False),
        Column('description', String(1000), nullable=False,
               default='No description'
               ),
        Column('last_checked_in', DateTime, nullable=False,
               default=datetime.utcnow()),
        Column('heartbeat_timeout_seconds', Integer,
               nullable=False, default=30),
        Column('is_service_available', Boolean, nullable=False),
        Column(
            'job_registration_schema',
            JSON, nullable=False,
            default=_GENERAL_JSON_SCHEMA
        ),
        Column(
            'job_result_schema',
            JSON,
            nullable=False,
            default=_GENERAL_JSON_SCHEMA
        )
    )

    _jobs = Table(
        'jobs', _metadata,
        Column('job_id', UUID, primary_key=True, nullable=False),
        Column('service_id', UUID, ForeignKey('services.service_id'),
               nullable=False
               ),
        Column('date_submitted', DateTime, nullable=False,
               default=datetime.utcnow()),
        Column('status', Enum(JobStatus), default=JobStatus.REGISTERED),
        Column('parameters', JSON, nullable=False),
        Column('results', JSON, nullable=True),
        Column('job_set_id', ForeignKey('job_sets.job_set_id'), nullable=True)
    )

    _job_sets = Table(
        'job_sets', _metadata,
        Column('job_set_id', UUID, primary_key=True, nullable=False),
        Column('description', String(140), nullable=False)
    )

    @property
    def services(self) -> Table:
        """

        :return: The services table
        """
        return self._services

    @property
    def job_sets(self) -> Table:
        """

        :return: The table containing job sets
        """
        return self._job_sets

    @property
    def jobs(self) -> Table:
        """

        :return: The jobs table
        """
        return self._jobs

    @property
    def metadata(self) -> MetaData:
        """

        :return: The SQLAlchemy metadata
        """
        return self._metadata

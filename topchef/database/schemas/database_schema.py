from .abstract_database_schemas import AbstractDatabaseSchema
from datetime import datetime
from sqlalchemy import Table, Column, MetaData, String, Boolean, Integer
from sqlalchemy import DateTime, ForeignKey, Enum
from ..uuid_database_type import UUID


class DatabaseSchema(AbstractDatabaseSchema):
    """
    Describes the schema for the database
    """
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
        Column('job_registration_schema_id', UUID, nullable=False),
        Column('job_result_schema_id', UUID, nullable=False)
    )

    _jobs = Table(
        'jobs', _metadata,
        Column('job_id', UUID, primary_key=True, nullable=False),
        Column('service_id', UUID, ForeignKey('services.service_id'),
               nullable=False
               ),
        Column('date_submitted', DateTime, nullable=False,
               default=datetime.utcnow()),
        Column('status', Enum("REGISTERED", "WORKING", "COMPLETED", "ERROR"),
               default="REGISTERED"),
        Column('parameters_id', UUID, nullable=False),
        Column('results_id', UUID, nullable=False),
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

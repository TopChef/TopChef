"""
Contains different database schemas used to represent data
"""
from .abstract_database_schema import AbstractDatabaseSchema
from .database_schema import DatabaseSchema
from .job_status import JobStatus

database = DatabaseSchema()

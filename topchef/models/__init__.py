"""
Describes the model classes that are to be written to some persistent
storage. These model classes may make dirty changes to persistent storage,
but they are not responsible for committing any changes that they make.
"""
from .abstract_service import AbstractService
from .abstract_job import AbstractJob
from .job import Job

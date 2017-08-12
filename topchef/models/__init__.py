"""
Describes the model classes that are to be written to some persistent
storage. These model classes may make dirty changes to persistent storage,
but they are not responsible for committing any changes that they make.
"""
from .interfaces import Job
from .interfaces import JobList
from .interfaces import Service
from .interfaces import ServiceList
from .interfaces import APIMetadata
from .interfaces import APIError

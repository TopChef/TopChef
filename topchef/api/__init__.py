"""
Contains the Flask blueprint for the API
"""
from .api_metadata import APIMetadata
from .services_list import ServicesList
from .service_detail import ServiceDetailForServiceID as ServiceDetail
from .jobs_list import JobsList
from .jobs_for_service import JobsForServiceID as JobsForService
from .job_queue import JobQueueForServiceID as JobQueueForService
from .next_job import NextJobForServiceID as NextJob
from .job_detail import JobDetailForJobID as JobDetail
from .validator import JSONSchemaValidator

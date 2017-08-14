"""
Contains the Flask blueprint for the API
"""
from .api_metadata import APIMetadata
from .services_list import ServicesList
from .service_detail import ServiceDetailForServiceID as ServiceDetail
from .jobs_list import JobsList

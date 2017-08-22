"""
Contains all the :mod:`marshmallow` schemas used in the API. These are the
templates for entering in data into the API, and have a role similar to
forms in conventional web applications. Marshmallow handles the error
checking and reporting.
"""
from .json_schema import JSONSchema
from .api_metadata import APIMetadata
from .new_service import NewService
from .service_overview import ServiceOverview
from .api_exception import APIException
from .service_detail import ServiceDetail
from .job_overview import JobOverview
from .job_detail import JobDetail
from .job_modification import JobModification
from .json_schema_validator import JSONSchemaValidator
from .service_modifier import ServiceModification
from .new_job import NewJob

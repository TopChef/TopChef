"""
Contains implementations of all API exceptions that can be thrown by the API
and exposed to the user. Each class in this folder is an instance of
``APIException``. Since ``APIException`` is an instance of ``Exception``,
these errors can be thrown as well. Each exception has an HTTP status code
associated with it, a title, and a message. The HTTP endpoints can use these
attributes to prepare error reports for the API consumer.
"""
from .method_not_allowed_error import MethodNotAllowedError
from .sqlalchemy_error import SQLAlchemyError
from .service_not_found_error import ServiceWithUUIDNotFound
from .not_uuid_error import NotUUIDError
from .deserialization_error import DeserializationError
from .serialization_error import SerializationError
from .request_not_json_error import RequestNotJSONError
from .job_with_uuid_not_found_error import JobWithUUIDNotFound
from .jsonschema_validation_error import ValidationError

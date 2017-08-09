"""
Contains implementations of all API exceptions that can be thrown by the API
"""
from .method_not_allowed_exception import MethodNotAllowedException
from .sqlalchemy_exception import SQLAlchemyException
from .service_not_found_exception import ServiceWithUUIDNotFound
from .not_uuid_error import NotUUIDError
from .deserialization_error import DeserializationError
from .serialization_error import SerializationError

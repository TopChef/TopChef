"""
Contains a model for a TopChef API exception
"""
from topchef.models.interfaces.api_exception import APIException as \
    APIExceptionInterface


class APIException(Exception, APIExceptionInterface):
    """
    Base class for an API exception
    """
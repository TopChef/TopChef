"""
Contains a model for a TopChef API exception
"""
from topchef.models.interfaces.api_error import APIError as \
    APIErrorInterface


class APIError(APIErrorInterface):
    """
    Base class for an API exception
    """

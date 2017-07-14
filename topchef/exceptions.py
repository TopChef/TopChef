"""
Contains exceptions that can be thrown
"""


class NoPasswordError(AttributeError):
    """
    Thrown if the getter for the password is retrieved
    """
    pass

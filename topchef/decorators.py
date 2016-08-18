"""
Contains useful decorator functions
"""
from functools import wraps
from flask import request, jsonify


def check_json(f):
    """
    Checks that the request body is written in Javascript Object Notation
    (JSON). If it is not, a 400 response is returned. Otherwise, return the
    normal output

    :param callable f: The function to decorate
    :return: The appropriate Flask response
    :rtype: flask.Response
    """
    @wraps(f)
    def checked_endpoint(*args, **kwargs):
        if not request.json:
            response = jsonify({'errors': 'The request body is not JSON'})
            response.status_code = 400
            return response
        else:
            return f(*args, **kwargs)

    return checked_endpoint
"""
Middleware layer that allows for method override.

This was taken from
http://flask.pocoo.org/docs/0.12/patterns/methodoverrides/
"""


class HTTPMethodOverrideMiddleware(object):
    """
    Middleware layer allowing method override
    """
    allowed_methods = frozenset([
        'GET',
        'HEAD',
        'POST',
        'DELETE',
        'PUT',
        'PATCH',
        'OPTIONS'
    ])
    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app):
        """

        :param app: The WSGI application for which method override is to be
            enabled.
        """
        self.app = app

    def __call__(self, environ, start_response):
        """

        :param environ: The request environment
        :param start_response: The response to be returned
        :return: The result of calling the application with the given
            request environment and response object
        """
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if method in self.allowed_methods:
            environ['REQUEST_METHOD'] = method

        if method in self.bodyless_methods:
            print("bodyless method conditional hit")
            environ['CONTENT_LENGTH'] = '0'

        return self.app(environ, start_response)

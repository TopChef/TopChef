"""
This module tests that requests sent with an
``X-HTTP-METHOD-OVERRIDE`` header will result in a request of the type
 specified by the header, not the HTTP verb
"""
import pytest
import multiprocessing
import time
import requests
from topchef.api_server import app

TESTING_HOST = 'localhost'
TESTING_PORT = 41251


@pytest.yield_fixture(scope='module')
def flask_app():
    """
    Start the server process on a high port, and in a separate process
    """
    server = multiprocessing.Process(
        target=app.run,
        kwargs={'host': TESTING_HOST, 'port': TESTING_PORT, 'debug': True}
    )

    server.start()

    time.sleep(3)  # Give the server some time to start

    assert server.is_alive()

    base_url = 'http://%s:%s' % (TESTING_HOST, TESTING_PORT)

    yield base_url

    server.terminate()

    time.sleep(3)

    assert not server.is_alive()


def test_post(flask_app):
    """
    POST should not be allowed on the root endpoint, but we're going to
    overload it with a ``GET`` request using the method override header.
    That request should go through

    :param flask_app: The opened application to use for the test
    """
    response = requests.post(
        flask_app
    )

    assert response.status_code == 405

    response = requests.post(
        flask_app, headers={"X-HTTP-METHOD-OVERRIDE": "GET"}
    )

    assert response.status_code == 200

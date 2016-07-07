import pytest
from topchef.api_server import app
from contextlib import contextmanager


@contextmanager
def app_client(endpoint):
    app_client = app.test_client()
    request_context = app.test_request_context()

    request_context.push()

    yield app_client

    request_context.pop()


@pytest.mark.parametrize('endpoint', ['/', '/services'])
def test_getter(endpoint):
    with app_client(endpoint) as client:
        response = client.get(
            endpoint, headers={'Content-Type': 'application/json'}
        )

    assert response.status_code == 200
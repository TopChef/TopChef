import pytest
from topchef.api_server import app

@pytest.fixture
def client():
    client = app.test_client()
    return client

def test_api_server(client):
    response = client.get('/')
    assert response.status_code == 200

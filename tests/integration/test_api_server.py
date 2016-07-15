import json
import requests
from .fixtures import SERVER_HOST, SERVER_PORT
from .fixtures import SERVICE_NAME, SERVICE_DESCRIPTION, SERVICE_SCHEMA
from .fixtures import database, api_server, service, service_in_database


def test_post_service(service, api_server):
    request_body = {
        "name": SERVICE_NAME,
        "description": SERVICE_DESCRIPTION,
        "schema": SERVICE_SCHEMA
    }

    response = requests.post(
        'http://%s:%s/services' % (SERVER_HOST, SERVER_PORT),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(request_body)
    )

    assert response.status_code == 201
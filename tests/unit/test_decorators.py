import pytest
import json
from flask import jsonify, Flask
from topchef.decorators import check_json
from uuid import uuid4


@pytest.yield_fixture()
def fake_endpoint():

    endpoint_name = '/%s' % str(uuid4())

    app = Flask(__name__)

    @app.route(endpoint_name, methods=["POST"])
    @check_json
    def endpoint():
        return jsonify({'status': 'success'})

    request_context = app.test_request_context()
    request_context.push()

    client = app.test_client()

    yield client, endpoint_name

    request_context.pop()


def test_decorator_no_json(fake_endpoint):
    client = fake_endpoint[0]
    endpoint_name = fake_endpoint[1]

    response = client.post(endpoint_name)
    assert response.status_code == 400


def test_decorator_json(fake_endpoint):
    client = fake_endpoint[0]
    endpoint_name = fake_endpoint[1]

    data_to_post = json.dumps({'data': 'in JSON'})

    response = client.post(
        endpoint_name, headers={'content-type': 'application/json'},
        data=data_to_post
    )

    assert response.status_code == 200

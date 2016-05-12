import pytest
from topchef.api_server import app

username = 'foo'
job_id = 1

@pytest.fixture
def client():
    client = app.test_client()
    return client


def framework(client, url):
    response = client.get(url)
    assert response.status_code == 200


def test_hello_world(client):
    framework(client, '/')


def test_get_users(client):
    framework(client, '/users')


def test_post_users(client):
    response = client.post('/users')
    assert response.status_code == 200


def test_get_user_info(client):
    response = client.get('/users/%s' % username)
    assert response.status_code == 200


def test_get_jobs_for_user(client):
    framework(client, '/users/%s/jobs' % username)


def test_make_job_for_user(client):
    response = client.post('/users/<username>/jobs')
    assert response.status_code == 200


def test_get_job_details(client):
    framework(client, '/users/%s/jobs/%d' % (username, job_id))


def test_get_next_job(client):
    framework(client, '/users/%s/jobs/next' % username)


def test_do_stuff_to_job(client):
    response = client.patch('/users/%s/jobs/%d' % (username, job_id))
    assert response.status_code == 200


def test_get_programs(client):
    framework(client, '/programs')


def test_get_program_by_id(client):
    framework(client, '/programs/1')
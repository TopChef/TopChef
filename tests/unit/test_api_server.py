import pytest
from topchef.api_server import app
from topchef.models import User
import json

username = 'foo'
job_id = 1

@pytest.fixture
def client():
    client = app.test_client()
    return client

@pytest.fixture
def user():
    user = User('test_user', 'test-user@test-user.com')
    return user


def framework(client, url):
    response = client.get(url)
    assert response.status_code == 200


def test_hello_world(client):
    framework(client, '/')


def test_get_users(client, user, monkeypatch):
    monkeypatch.setattr('sqlalchemy.orm.query.Query.all', lambda x: [user])
    framework(client, '/users')


class TestPostUsers(object):
    def test_post_users(self, client, user, monkeypatch):
        def patch_all():
            return [user]

        monkeypatch.setattr('sqlalchemy.orm.query.Query.first', patch_all)
        monkeypatch.setattr('sqlalchemy.orm.session.Session.commit', lambda x: True)
        response = client.post(
            '/users', data=json.dumps(user.UserSchema().dump(user).data), headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 201


def test_get_user_info(client, user, monkeypatch):
    monkeypatch.setattr('sqlalchemy.orm.query.Query.first', lambda x: user)
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
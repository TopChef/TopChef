import pytest
from topchef.api_server import app
from topchef.models import User, Job
import json
from datetime import datetime

username = 'foo'
job_id = 1

@pytest.fixture
def client():
    client = app.test_client()
    return client

@pytest.fixture
def user():
    user = User('test_user', 'test-user@test-user.com')
    user.from_session = lambda x: user
    return user

@pytest.fixture
def job():
    job = Job(1, datetime.utcnow())
    job.id = 1
    job.job_owner = user()
    return job

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
            '/users', data=json.dumps(user.UserSchema().dump(user).data),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 201


def test_get_user_info(client, user, monkeypatch):
    monkeypatch.setattr('sqlalchemy.orm.query.Query.first', lambda x: user)
    response = client.get('/users/%s' % username)
    assert response.status_code == 200


class TestGetJobsForUser(object):
    def test_get_jobs_for_user(self, client, user, monkeypatch):
        monkeypatch.setattr('topchef.models.User.jobs', [])
        monkeypatch.setattr('topchef.models.User.from_session', lambda x, session: user)
        framework(client, '/users/%s/jobs' % username)

    def test_get_jobs_no_user(self, client, monkeypatch):
        def kaboom(*args):
            raise User.UnableToFindItemError('Kaboom')

        monkeypatch.setattr('topchef.models.User.from_session', kaboom)
        response = client.get('/users/foo/jobs')
        assert response.status_code == 404


def test_make_job_for_user(client, user, monkeypatch, job):
    monkeypatch.setattr(
        'topchef.models.User.from_session',
        lambda x, session: user
    )
    monkeypatch.setattr(
        'sqlalchemy.orm.Session.add', lambda *args: None
    )
    monkeypatch.setattr(
        'sqlalchemy.orm.Session.commit', lambda *args: None
    )

    response = client.post(
        '/users/foo/jobs',
        data=job.JobSchema().dumps(job).data,
        headers={'Content-Type': 'application/json'}
    )

    assert response.status_code == 201


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
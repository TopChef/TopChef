"""
Contains unit tests for :mod:`topchef.api_server`
"""
import pytest
from topchef.api_server import app
from topchef.models import User
import json

username = 'foo'
job_id = 1


@pytest.fixture
def client():
    """
    Create a test client and return it

    :return: The flask test client
    """
    client = app.test_client()
    return client


@pytest.fixture
def user():
    """
    Return a test user for use in the test case

    :return: A test user
    :rtype: :class:`topchef.models.User`
    """
    user = User('test_user', 'test-user@test-user.com')
    return user


def framework(client, url):
    """
    Run a simple test case to get data from a server. Runs through the API
    endpoint along the happy path

    :param client: The test client that will make the HTTP request
    :param str url: The URL to which the request will be made
    """
    response = client.get(url)
    assert response.status_code == 200


def test_hello_world(client):
    """
    Run the framework on the root endpoint
    """
    framework(client, '/')


def test_get_users(client, user, monkeypatch):
    """
    Test that the endpoint successfully gets all users
    :param client: The test client
    :param user: The test yser fixture
    :param monkeypatch: A utility which allows for replacement of functions
        with another definition
    """
    monkeypatch.setattr('sqlalchemy.orm.query.Query.all', lambda x: [user])
    framework(client, '/users')


class TestPostUsers(object):
    """
    Wrapper for test related to the ``POST`` request at the ``/users`` endpoint
    """
    def test_post_users(self, client, user, monkeypatch):
        """
        Test the happy path, and assert the return code is 201
        :param client: The test client
        :param user: The test user
        :param monkeypatch: The monkeypatching system in ``py.test``
        """
        def patch_all():
            return [user]

        monkeypatch.setattr('sqlalchemy.orm.query.Query.first', patch_all)
        monkeypatch.setattr('sqlalchemy.orm.session.Session.commit', lambda x: True)
        response = client.post(
            '/users', data=json.dumps(user.UserSchema().dump(user).data),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 201


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
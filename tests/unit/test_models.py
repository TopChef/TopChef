"""
Contains tests for :mod:`topchef.models`
"""
import pytest
import mock
from topchef.models import User, UnableToFindItemError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


@pytest.fixture
def test_session():
    return Session(bind=create_engine('sqlite:///'))


class TestUser(object):
    username = 'charmander'
    email = 'charmander@oak.com'

    @staticmethod
    @pytest.fixture
    def user():
        return User(TestUser.username, TestUser.email)

    class TestFromSession(object):

        def test_from_user_happy_path(self, user, test_session):
            with mock.patch('sqlalchemy.orm.Query.first', return_value=user):
                returned_user = user.__class__.from_session(
                    user.username, test_session
                )

            assert returned_user == user

        @mock.patch('sqlalchemy.orm.Query.first', return_value=None)
        def test_from_user_no_user(self, mock_first, user, test_session):
            with pytest.raises(UnableToFindItemError):
                user.__class__.from_session(user.username, test_session)

            assert mock_first.called


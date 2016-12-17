"""
Contains unit tests for :meth:`topchef.api_server.register_service`
"""
import json
import mock
from sqlalchemy.exc import IntegrityError
from tests.unit.test_api_server import UnitTestWithService


class TestRegisterService(UnitTestWithService):
    """
    Contains unit tests for the method
    """
    @property
    def endpoint(self):
        return '/services'

    @mock.patch('sqlalchemy.orm.session.Session.commit')
    def test_post_service(self, mock_commit, _app_client):
        endpoint = '/services'
        response = _app_client.post(
            endpoint, headers={'Content-Type': 'application/json'},
            data=json.dumps(self._job_registration_schema)
        )

        assert response.status_code == 201
        assert mock_commit.called

    @mock.patch('sqlalchemy.orm.session.Session.commit',
                side_effect=IntegrityError(
                    "Testing for kaboom", orig='here', params='data')
                )
    @mock.patch('sqlalchemy.orm.session.Session.rollback')
    def test_post_service_integrity_error(self, mock_rollback, mock_commit,
                                          _app_client):
        response = _app_client.post(
            self.endpoint, headers=self.headers,
            data=json.dumps(self._job_registration_schema)
        )

        assert response.status_code == 400
        assert json.loads(response.data)['errors']['case_number']
        assert mock_commit.called
        assert mock_rollback.called

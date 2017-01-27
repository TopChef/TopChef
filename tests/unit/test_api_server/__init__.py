"""
Contains unit tests for :mod:`topchef.api_server`
"""
import abc
import pytest
import json
from tests.unit import UnitTest as _BaseUnitTest
from uuid import UUID


class UnitTest(_BaseUnitTest):
    """
    Base class for all tests of the module
    """
    __metaclass__ = abc.ABCMeta

    status_codes = {
        'success': 200,
        'created': 201,
        'not found': 404
    }


class UnitTestWithService(UnitTest):
    """
    Base class for unit tests that require a service to be posted
    """
    __metaclass__ = abc.ABCMeta

    _services_endpoint = '/services'
    service_name = "TestService"
    service_id = None

    bad_service_name = "InvalidService"

    _template_endpoint = '/services/%s'

    @property
    def endpoint(self): return self._services_endpoint

    _job_registration_schema = {
        "name": service_name,
        "description": "A service created for unit testing",
        "job_registration_schema": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 10
                }
            }
        }
    }

    _valid_job_schema = {'parameters': {'value': 1}}
    _invalid_job_schema = {'parameters': {'value': 100}}

    @pytest.yield_fixture
    def _posted_service(self, _app_client, _database):
        response = _app_client.post(
            self._services_endpoint, headers=self.headers,
            data=json.dumps(self._job_registration_schema)
        )

        if response.status_code != self.status_codes['created']:
            raise RuntimeError(
                'Unable to post testing service, server returned %d' %
                response.status_code
            )

        data = json.loads(response.data.decode('utf-8'))

        self.service_id = UUID(data['data']['service_details']['id'])

        yield _app_client


class UnitTestWithJob(UnitTestWithService):
    """
    Base class for unit tests that also have a posted job
    """

    job_name = "Testing Job"
    _job_id = None

    _jobs_poster_template = '/services/%s/jobs'

    @property
    def job_id(self):
        return self._job_id

    @pytest.yield_fixture
    def _posted_job(self, _posted_service):
        response = _posted_service.post(
            self._jobs_poster_template % self.service_id, headers=self.headers,
            data=json.dumps(self._valid_job_schema)
        )

        data = json.loads(response.data.decode('utf-8'))
        self._job_id = UUID(data['data']['job_details']['id'])

        yield _posted_service

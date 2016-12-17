"""
Contains unit tests for :mod:`topchef.api_server`
"""
import abc
import pytest
import json
from tests.unit import UnitTest as _BaseUnitTest


class UnitTest(_BaseUnitTest):
    """
    Base class for all tests of the module
    """
    __metaclass__ = abc.ABCMeta

    status_codes = {
        'success': 200,
        'created': 201
    }


class UnitTestWithService(UnitTest):
    """
    Base class for unit tests that require a service to be posted
    """
    __metaclass__ = abc.ABCMeta

    _services_endpoint = '/services'

    @property
    def endpoint(self): return self._services_endpoint

    _job_registration_schema = {
        "name": "TestService",
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

        yield _app_client
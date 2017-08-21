"""
Contains unit tests for :mod:`topchef.api.api_metadata`
"""
import json
import unittest
import unittest.mock as mock
from topchef.api.api_metadata import APIMetadata
from topchef.wsgi_app import TestingWSGIAPPFactory
from topchef.models import APIMetadata as MetadataInterface
from topchef.serializers import APIMetadata as MetadataSerializer
from tests.unit.model_generators.api_metadata import api_metadata
from sqlalchemy.orm import Session
from hypothesis import given
from flask import Request


class TestAPIMetadata(unittest.TestCase):
    """
    Base class for testing the module
    """
    def setUp(self) -> None:
        """
        Set up a mock session and push a testing application context for Flask
        """
        self.session = mock.MagicMock(spec=Session)  # type: Session
        self.request = mock.MagicMock(spec=Request)  # type: Request

        self.testing_app = TestingWSGIAPPFactory().app

        self._app_context = self.testing_app.test_request_context()
        self._app_context.push()

    def tearDown(self) -> None:
        """
        Pop the testing context
        """
        self._app_context.pop()


class TestGet(TestAPIMetadata):
    """
    Contains unit tests for the ``get`` method in the endpoint
    """
    @given(api_metadata())
    def test_get(self, metadata: MetadataInterface) -> None:
        """

        :param metadata:
        :return:
        """
        endpoint = APIMetadata(
            self.session, flask_request=self.request, metadata=metadata
        )
        response = endpoint.get()
        self.assertEqual(200, response.status_code)
        self.assert_data_equal(
            json.loads(response.data.decode('utf-8')), metadata
        )

    def assert_data_equal(
            self, data: dict, metadata: MetadataInterface
    ) -> None:
        """

        :param data: The data from the endpoint to check
        :param metadata: The metadata against which the data is to be checked
        """
        self.assertEqual(
            data['data'], self._get_dict_for_metadata_model(metadata)
        )

    @staticmethod
    def _get_dict_for_metadata_model(metadata: MetadataInterface) -> dict:
        return MetadataSerializer().dump(metadata, many=False).data

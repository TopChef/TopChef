"""
Contains unit tests for :mod:`topchef.serializers.new_service
"""
import unittest
import unittest.mock as mock
from topchef.models import Service
from topchef.serializers import NewService
from hypothesis import given
from hypothesis.strategies import dictionaries, text


class TestNewServiceSerializer(unittest.TestCase):
    """
    Base class for unit testing the serializer
    """
    def setUp(self) -> None:
        """
        Set up the serializer
        """
        self.service = mock.MagicMock(spec=Service)
        self.serializer = NewService()


class TestSerializationOfFields(TestNewServiceSerializer):
    """
    Tests that the serializer can serialize services correctly
    """
    @given(
        text(),
        text(),
        dictionaries(text(), text()),
        dictionaries(text(), text())
    )
    def test_load(
            self, name: str, description: str, job_registration_schema: dict,
            job_result_schema: dict
    ) -> None:
        """
        Tests that randomly-generated valid data is de-serialized correctly

        :param name: The name of the service
        :param description: The service description
        :param job_registration_schema: The service job registration schema
        :param job_result_schema: The service result schema
        """
        self.set_variables_for_model(
            name, description, job_registration_schema, job_result_schema
        )
        data, errors = self.serializer.load(
            self.get_expected_data(name, description,
                                   job_registration_schema, job_result_schema)
        )
        self.assertEqual(errors, {})
        self.assertEqual(
            data,
            self.get_expected_data(
                name, description, job_registration_schema, job_result_schema
            )
        )

    def set_variables_for_model(
            self, name: str, description: str, job_registration_schema: dict,
            job_result_schema: dict
    ) -> None:
        self.service.name = name
        self.service.description = description,
        self.service.job_registration_schema = job_registration_schema
        self.service.job_result_schema = job_result_schema

    @staticmethod
    def get_expected_data(
            name: str,
            description: str,
            job_registration_schema: dict,
            job_result_schema: dict
    ) -> dict:
        return {
            'name': name,
            'description': description,
            'job_registration_schema': job_registration_schema,
            'job_result_schema': job_result_schema
        }


"""
Contains integration tests for TopChefModels
"""
from tests.integration import IntegrationTestCase
from topchef.models.service import Service


class IntegrationTestCaseWithModels(IntegrationTestCase):
    @classmethod
    def setUpClass(cls):
        IntegrationTestCase.setUpClass()
        cls.service = cls._create_test_service()
        cls.job = cls._create_test_job()

    @classmethod
    def _create_test_service(cls):
        service_name = 'Test description'
        service_description = 'Integration test for services'
        job_registration_schema = {'type': 'object'}
        job_result_schema = {'type': 'object'}

        if hasattr(cls, 'session'):
            return Service.new(
                service_name, service_description, job_registration_schema,
                job_result_schema, cls.session
            )
        else:
            raise AttributeError('The class %s must have a DB session', cls)

    @classmethod
    def _create_test_job(cls):
        job_parameters = {'value': 1}

        if hasattr(cls, 'service'):
            return cls.service.new_job(job_parameters)

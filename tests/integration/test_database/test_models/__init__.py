from abc import ABCMeta

from tests.integration import IntegrationTestCase
from uuid import uuid4
from sqlalchemy.orm import Session
from topchef.database.models import Service


class IntegrationTestCaseWithService(IntegrationTestCase, metaclass=ABCMeta):
    """
    Base class for integration tests, with a service already built
    """

    @classmethod
    def setUpClass(cls):
        IntegrationTestCase.setUpClass()
        cls.service_id = uuid4()
        cls.service_name = 'Service'
        cls.service_description = 'description'

        cls.job_registration_schema = {
            'type': 'object',
            'properties': {
                'value': {
                    'type': 'integer',
                    'minimum': 1,
                    'maximum': 10
                }
            }
        }

        cls.valid_job_registration = {'value': 5}
        cls.invalid_job_registration = {'value': 11}

        cls.job_result_schema = {
            'type': 'object',
            'properties': {
                'result': {
                    'type': 'integer',
                    'minimum': 11,
                    'maximum': 21
                }
            }
        }

        cls.valid_result = {'result': 16}
        cls.invalid_result = {'result': 2123213}

        cls.service = Service(
            cls.service_id, cls.service_name, cls.service_description,
            cls.job_registration_schema, cls.job_result_schema
        )

        cls._write_service(cls.service, cls.session)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'service'):
            cls._delete_service(cls.service, cls.session)

    @classmethod
    def _write_service(cls, service: Service, session: Session) -> None:
        session.add(service)
        cls._safely_commit_session(session)

    @classmethod
    def _delete_service(cls, service: Service, session: Session) -> None:
        session.delete(service)
        cls._safely_commit_session(session)

    @staticmethod
    def _safely_commit_session(session: Session):
        try:
            session.commit()
        except:
            session.rollback()
            raise

from marshmallow import Schema, fields
from sqlalchemy.orm import Session, sessionmaker

from tests.acceptance.test_cases.acceptance_test_case import AcceptanceTestCase
from topchef import APP_FACTORY
from topchef.models.service_list import ServiceList
from topchef.serializers import JSONSchema


class AcceptanceTestCaseWithService(AcceptanceTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        """
        Add a service to the DB
        """
        AcceptanceTestCase.setUpClass()
        cls.service_name = 'Testing Service'
        cls.description = 'Description for the Testing Service'

        cls.job_registration_schema = JSONSchema(
            title='Job Registration Schema',
            description='Must be fulfilled for an experiment'
        ).dump(cls.JobRegistrationSchema())

        cls.job_result_schema = JSONSchema(
            title='Job Result Schema',
            description='Must be fulfilled to post results'
        ).dump(cls.JobRegistrationSchema())

        session = Session(bind=APP_FACTORY.engine, expire_on_commit=False)

        service_list = ServiceList(session)
        cls.service = service_list.new(
            cls.service_name, cls.description, cls.job_registration_schema,
            cls.job_result_schema
        )
        session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Delete the service from the DB
        """
        if hasattr(cls, 'service'):
            session = Session(bind=APP_FACTORY.engine)
            service_list = ServiceList(session)
            del service_list[cls.service.id]
        AcceptanceTestCase.tearDownClass()

    class JobRegistrationSchema(Schema):
        value = fields.Int()

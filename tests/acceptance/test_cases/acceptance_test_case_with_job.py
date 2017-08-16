from .acceptance_test_case_with_service import AcceptanceTestCaseWithService
from sqlalchemy.orm import Session


class AcceptanceTestCaseWithJob(AcceptanceTestCaseWithService):
    """
    Base class for an acceptance test with a service and a job for that
    service being submitted to the DB
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Add a job to the DB
        """
        AcceptanceTestCaseWithService.setUpClass()
        cls.valid_job_schema = {'value': 1}
        cls.job = cls.service.new_job(cls.valid_job_schema)
        Session.object_session(cls.service.db_model).commit()

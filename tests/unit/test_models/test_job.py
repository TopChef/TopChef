"""
Contains unit tests for :mod:`topchef.models.job
"""
from uuid import uuid4
import unittest
from unittest import mock
from topchef.models import Job
from topchef.database import Job as DatabaseJob
from sqlalchemy.orm import Session


class TestJob(unittest.TestCase):
    """
    Base class for unit testing :mod:`topchef.models.Job`
    """
    def setUp(self):
        self.job_id = uuid4()
        self.parameters = {'type': 'object'}
        self.results = {'light_count': 152}
        self.job = Job(self.job_id, self.parameters, self.results)

        self.database_session = mock.MagicMock(spec=Session)
        self.storage = mock.MagicMock()
        self.db_model = mock.MagicMock(spec=DatabaseJob)


class TestFromStorage(TestJob):
    """
    Contains unit tests for running things from storage
    """
    def test_from_storage(self):
        job = Job.from_storage(
            self.job_id, self.database_session, self.storage
        )
        self.assertEqual(
            job.id,
            self.database_session.query(DatabaseJob).filter_by(
                id=self.job_id).first().id
        )
        self.assertEqual(
            self.storage[self.db_model.parameters_id], job.parameters
        )
        self.assertEqual(
            job.results,
            self.storage[self.db_model.results_id]
        )

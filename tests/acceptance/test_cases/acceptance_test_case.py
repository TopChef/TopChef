"""
Base class for acceptance tests of the API. Acceptance tests run on the
entire server stack, and check that TopChef works end-to-end
"""
import unittest
from topchef import APP_FACTORY
from topchef.database.schemas.database_schema import DatabaseSchema
import multiprocessing as mp


class AcceptanceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = 'localhost'
        cls.port = 60123
        cls.protocol = 'http'
        cls.app = APP_FACTORY.app
        cls.app_process = mp.Process(target=cls.app.run)
        cls.app_process.daemon = True
        cls.app_process.start()

        cls._create_database(APP_FACTORY.engine)

    @classmethod
    def tearDownClass(cls):
        cls._drop_database(APP_FACTORY.engine)

        if hasattr(cls, 'app_process'):
            cls.app_process.terminate()
            _ = cls.app_process.exitcode

    @property
    def app_url(self) -> str:
        return '%s://%s:%s' % (self.protocol, self.host, self.port)

    def setUp(self):
        self.client = self.app.test_client()

    @classmethod
    def _create_database(cls, engine):
        """

        :param engine: The SQLAlchemy engine at which the DB is to be created
        """
        schema = DatabaseSchema()
        schema.metadata.create_all(bind=engine)

    @classmethod
    def _drop_database(cls, engine):
        """

        :param engine: The SQLAlchemy engine to be used to drop the DB
        """
        schema = DatabaseSchema()
        schema.metadata.drop_all(bind=engine)

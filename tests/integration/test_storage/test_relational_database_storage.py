import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from topchef.database.schemas import DatabaseSchemaWithJSONTable
from topchef.storage import RelationalDatabaseStorage, JSONDocument
from typing import Set


class TestRelationalDbStorage(unittest.TestCase):
    """
    Test that the relational DB storage works correctly
    """
    def setUp(self):
        self.engine = create_engine('sqlite://')
        self.session_factory = sessionmaker(bind=self.engine)
        self.database = DatabaseSchemaWithJSONTable()
        self.database.metadata.create_all(bind=self.engine)

        self.storage = RelationalDatabaseStorage(self.session_factory)

    def tearDown(self):
        self.database.metadata.drop_all(bind=self.engine)


class TestRelationalDbWithService(TestRelationalDbStorage):
    def setUp(self):
        TestRelationalDbStorage.setUp(self)
        self.parameter_schema = {'type': 'object'}
        self.result_schema = {'type': 'result'}

        self.parameter_document = JSONDocument(self.parameter_schema)
        self.result_document = JSONDocument(self.result_schema)

        self._add_documents_to_db(
            {self.parameter_document, self.result_document}
        )

    def _add_documents_to_db(self, documents: Set[JSONDocument]) -> None:
        session = self.session_factory()

        for document in documents:
            session.add(document)

        session.commit()


class TestGetItem(TestRelationalDbWithService):
    """

    """
    def test_getitem(self):
        document_from_db = self.storage[self.parameter_document.id]  # type:
        #  JSONDocument

        self.assertEqual(
            document_from_db, self.parameter_schema
        )

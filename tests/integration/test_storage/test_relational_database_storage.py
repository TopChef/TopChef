"""
Contains unit tests for the relational database storage
"""
from topchef.storage import JSONDocument
from typing import Iterable
from uuid import uuid4
from ..integration_test_case import IntegrationTestCase


class TestRelationalDbStorage(IntegrationTestCase):
    """
    Base class for unit testing the relational database storage
    """


class TestRelationalDbWithDocument(TestRelationalDbStorage):
    def setUp(self) -> None:
        """

        Create some JSON schemas, and add them to the database storage
        """
        TestRelationalDbStorage.setUp(self)
        self.parameter_schema = {'type': 'object'}
        self.result_schema = {'type': 'result'}

        self.parameter_document = JSONDocument(self.parameter_schema)
        self.result_document = JSONDocument(self.result_schema)

        self._add_documents_to_db(
            {self.parameter_document, self.result_document}
        )

    def _add_documents_to_db(self, documents: Iterable[JSONDocument]) -> None:
        """

        :param documents: The documents to write
        """
        session = self.session_factory()

        for document in documents:
            session.add(document)

        session.commit()


class TestGetItemWithDocument(TestRelationalDbWithDocument):
    """
    Contains unit tests for the document getter.
    """
    def setUp(self) -> None:
        """

        Create an invalid document ID to test that finding invalid documents
        doesn't work
        """
        TestRelationalDbWithDocument.setUp(self)
        self.invalid_document_id = uuid4()

    def test_getitem_document_exists(self) -> None:
        """
        Test that the document is correctly retrieved from storage if one
        exists
        """
        document_from_db = self.storage[
            self.parameter_document.id]  # type: JSONDocument

        self.assertEqual(
            document_from_db, self.parameter_schema
        )

    def test_getitem_no_document(self) -> None:
        """
        Test that the system fails correctly
        """
        with self.assertRaises(KeyError):
            _ = self.storage[self.invalid_document_id]


class TestSetItem(TestRelationalDbWithDocument):
    """
    Contains unit tests for the document setter
    """
    def setUp(self):
        """
        Create an invalid ID to test the KeyError scenario, and some fake
        document data that will be set in the new document
        """
        TestRelationalDbWithDocument.setUp(self)
        self.invalid_document_id = uuid4()

        self.new_document_data = {'foo': 'bar', 'bar': 'baz'}

    def test_setitem(self):
        """

        Test that the setter works correctly
        """
        self.storage[self.parameter_document.id] = self.new_document_data
        self.assertEqual(
            self.new_document_data,
            self.storage[self.parameter_document.id]
        )

    def test_setitem_no_document(self):
        """

        Test that the setter throws a ``KeyError`` if the document to be set
        does not exist
        """
        with self.assertRaises(KeyError):
            self.storage[self.invalid_document_id] = self.new_document_data


class TestDelItem(TestRelationalDbWithDocument):
    """
    Contains unit tests for the deleter
    """
    def test_delitem(self):
        """
        Test that the document is properly deleted
        """
        del self.storage[self.parameter_document.id]

        with self.assertRaises(KeyError):
            _ = self.storage[self.parameter_document.id]

"""
Contains unit tests for :mod:`topchef.database.uuid_database_type`
"""
import unittest
from topchef.database.uuid_database_type import UUID as DB_UUID
from uuid import UUID
from hypothesis import given
from hypothesis.strategies import uuids
from sqlalchemy.types import CHAR
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.dialects.sqlite.pysqlite import SQLiteDialect_pysqlite


class TestUUIDDatabaseType(unittest.TestCase):
    """
    Base class for unit testing the database type
    """
    def setUp(self):
        self.pg_sql_dialect = PGDialect_psycopg2()
        self.sqlite_dialect = SQLiteDialect_pysqlite()


class TestLoadDialectImpl(TestUUIDDatabaseType):
    """
    Tests the ``load_dialect_impl`` method
    """

    def test_name_postgresql(self) -> None:
        """
        Tests that if the name ``postgresql`` is passed into the UUID
        database type, then PostgreSQL's UUID type is loaded as a dialect for
        the UUID type.

        The returned type descriptor should be the same as the postgresql UUID
        database type
        """
        uuid_instance = DB_UUID()
        dialect_impl = uuid_instance.load_dialect_impl(self.pg_sql_dialect)
        self.assertIsInstance(
            dialect_impl, self.pg_sql_dialect.type_descriptor(
                postgresql.UUID()
            ).__class__
        )

    def test_name_sqlite(self) -> None:
        """
        Tests that if the name ``sqlite`` is given to the database, then a
        CHAR descriptor comes back out with 32 characters
        """
        uuid_instance = DB_UUID()
        dialect_impl = uuid_instance.load_dialect_impl(self.sqlite_dialect)
        self.assertIsInstance(
            dialect_impl, self.sqlite_dialect.type_descriptor(
                CHAR(32)
            ).__class__
        )


class TestProcessBindParam(TestUUIDDatabaseType):
    """
    Tests the ``process_bind_param`` method
    """
    def setUp(self):
        TestUUIDDatabaseType.setUp(self)
        self.expected_de_hyphenated_uuid_length = 32

    def test_value_is_none(self):
        db_uuid = DB_UUID()
        self.assertIsNone(db_uuid.process_bind_param(
            None, self.pg_sql_dialect)
        )
        self.assertIsNone(db_uuid.process_bind_param(
            None, self.sqlite_dialect
        ))

    @given(uuids())
    def bind_uuid_postgres(self, uuid: UUID) -> None:
        """
        Tests that if the UUID is passed to a Postgres dialect, that it is
        returned as a string with hyphens

        :param uuid: A randomly-generated UUID to store
        """
        db_uuid = DB_UUID()
        value_to_store = db_uuid.process_bind_param(
            uuid, self.pg_sql_dialect
        )
        self.assertEqual(value_to_store, str(uuid))

    @given(uuids())
    def bind_uuid_something_else(self, uuid: UUID) -> None:
        """
        Tests that the UUID gets de-hyphenated if using the CHAR 32 type, same
        as always.

        :param uuid: A randomly-generated UUID to store
        """
        db_uuid = DB_UUID()
        value_to_store = db_uuid.process_bind_param(
            uuid, self.sqlite_dialect
        )
        self.assertEqual(
            value_to_store, "%.32x" % int(uuid)
        )

    @given(uuids())
    def bind_uuid_not_uuid_type(self, uuid: UUID) -> None:
        """
        Tests that if the parameter to write in is a string that looks like
        a UUID, then it is written to the DB as a de-hyphenated UUID. This
        means that the id ``7490bda6-7c69-47c2-ad97-c7453f15811c`` gets written
        as ``7490bda67c6947c2ad97c7453f15811c``. The length of the
        de-hyphenated UUID MUST be 32 characters.

        :param uuid: The uuid to write, randomly generated
        """
        db_uuid = DB_UUID()
        value_to_store = db_uuid.process_bind_param(
            str(uuid), self.sqlite_dialect
        )
        self.assertEqual(
            value_to_store, value_to_store.replace('-', '')
        )
        self.assertEqual(
            self.expected_de_hyphenated_uuid_length,
            len(value_to_store)
        )

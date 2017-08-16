"""
In a similar vein to the JSON column type defined in
:mod:`topchef.database.json_type`, this type provides a back-end
agnostic way of storing Universally Unique Identifiers (UUIDs) in the
database. If the database is a Postgres DB, then it will use Postgres' UUID
data type to store the UUID. If such a type does not exist, then the UUID
will be stored as CHAR(32). This type represents a string that MUST have 32
characters.

This code was heavily inspired by SQLAlchemy's UUID type implementation,
as defined in :class:`sqlalchemy.types.TypeDecorator`.

"""
from sqlalchemy import TypeDecorator
from sqlalchemy.types import CHAR
from sqlalchemy import dialects
from sqlalchemy.dialects import postgresql
import uuid
from typing import Union, Optional

DialectType = Union[postgresql.UUID, CHAR]
ValueType = Optional[Union[uuid.UUID, str]]


class UUID(TypeDecorator):
    """
    Model class for the UUID type.
    impl represents the implementation to which this type will be forced
    when it is loaded from the DB
    """
    impl = CHAR

    def load_dialect_impl(self, dialect: dialects) -> DialectType:
        """
        SQLAlchemy wraps all database-specific features into
        dialects, which are then responsible for generating the SQL code
        for a specific DB type when loading in data. ``load_dialect_impl``
        is called when CRUD (create, update, delete operations) needs to be
        done on the database. This method is responsible for telling
        SQLAlchemy how to configure the dialect to write this type

        :param dialect: The loaded dialect
        :return: The type descriptor for this type.
        """
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(
            self, value: ValueType, dialect: dialects
    ) -> Optional[str]:
        """
        Given a value and a dialect, determine how to serialize the type to
        the dialect

        .. note::

            Python3 will complain that int is not supported for this type.
            I want to ignore this if possible

        :param value: The value to encode
        :param dialect: The dialect to which this will be encoded to
        :return: The value encoded in that dialect
        """
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % int(uuid.UUID(value))
            else:
                return "%.32x" % int(value)

    def process_result_value(
            self, value: Optional[str], dialect: dialects
    ) -> Optional[uuid.UUID]:
        """

        :param value: The value to process from the SQL query
        :param dialect: The dialect to use for the processing
        :return: The value as a UUID
        """
        if value is None:
            return value
        else:
            return uuid.UUID(value)

    def copy(self, *args, **kwargs) -> 'UUID':
        """

        :param args: The arguments to the UUID constructor
        :param kwargs: The keyword arguments to the UUID constructor
        :return: A deep copy of this object
        """
        return UUID(*args, **kwargs)

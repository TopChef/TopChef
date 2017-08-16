"""
SQL-based databases are strongly and statically typed. This means that every
variable must have a type associated with it, that type must be defined in
the schema, and the variable has that type for as long as this variable
exists. This definition implies that "changing the type" of a variable
(known as "casting") involves executing a function that maps one variable
and creates a new variable of a different type.

This module defines a backend-agnostic data type for storing JavaScript
Object Notation (JSON) objects in a relational database. Increasingly,
databases like MySQL and PostgreSQL are supporting JSON as a valid variable
type in their schemas. Using a JSON type to store JSON instead of a String
is a more elegant solution, as databases that support JSON make some effort
of checking that the JSON placed into a relational database is at least
syntactically correct. The type defined here will use a JSON type on MySQL
and PostgreSQL. If these types are not available, it will default into
storing the JSON as a string.
"""
from sqlalchemy import TypeDecorator
from sqlalchemy.types import VARCHAR
from sqlalchemy import dialects
from sqlalchemy.dialects import postgresql, mysql
import json
from typing import Union, Optional

DialectType = Union[postgresql.UUID, VARCHAR]
ValueType = Optional[Union[dict, str]]


class JSON(TypeDecorator):
    """
    Model class for the UUID type.
    impl represents the implementation to which this type will be forced
    when it is loaded from the DB
    """
    impl = VARCHAR
    _MAX_VARCHAR_LIMIT = 100000

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
            return dialect.type_descriptor(postgresql.JSON())
        elif dialect.name == 'mysql':
            if 'JSON' in dialect.ischema_names:
                return dialect.type_descriptor(mysql.JSON())
            else:
                return dialect.type_descriptor(
                    VARCHAR(self._MAX_VARCHAR_LIMIT)
                )
        else:
            return dialect.type_descriptor(VARCHAR(self._MAX_VARCHAR_LIMIT))

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
        else:
            return json.dumps(value)

    def process_result_value(
            self, value: Optional[str], dialect: dialects
    ) -> Optional[dict]:
        """

        :param value: The value to process from the SQL query
        :param dialect: The dialect to use for the processing
        :return: The value as a UUID
        """
        if value is None:
            return value
        else:
            return json.loads(value)

    def copy(self, *args, **kwargs) -> 'JSON':
        """

        :param args: The arguments to the UUID constructor
        :param kwargs: The keyword arguments to the UUID constructor
        :return: A deep copy of this object
        """
        return JSON(*args, **kwargs)

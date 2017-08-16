"""
The schema of a database is the set of all metadata that enables records to
be consistently entered into that database. By "consistent", what we mean is
that any operation not resulting in an error maps the database from one
valid state to another valid state. Unlike some no-SQL databases like
MongoDB, relational databases require that a schema is defined before
writing any records to the database. This module takes care of defining
that schema, using abstractions provided by SQLAlchemy. Based on this
schema and the particular database being used, SQLAlchemy can then generate
the SQL code needed to perform a particular manipulation on a database model.

the interface for the database schema is defined in
:mod:`.abstract_database_schema`. Each property there maps to a table in the
database.

"""
from .abstract_database_schema import AbstractDatabaseSchema
from .database_schema import DatabaseSchema
from .job_status import JobStatus

database = DatabaseSchema()

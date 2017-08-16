"""
This package contains the utilities required to map the state of the
resources managed by this API to the resources in a SQL-based database.
Using this package along with SQLAlchemy should allow querying of all the
resources in the database. This package alone DOES NOT guarantee that all
the models will be self-consistent, as this codebase allows resources to
span multiple storage systems. Since each type of resource is represented by
a model class, the onus is on the developer to make sure that resources are
consistent when loaded from multiple storage systems.

For example, if a ``Service`` has both a record in a MySQL database, and a
``job_registration_schema`` stored on a MongoDB instance, the ``Service``
model class would be responsible for ensuring that the MongoDB record and
the MySQL record agree.
"""
from .uuid_database_type import UUID
from .models import Job, Service, JobSet
from .schemas.abstract_database_schema import AbstractDatabaseSchema as \
    DatabaseSchema

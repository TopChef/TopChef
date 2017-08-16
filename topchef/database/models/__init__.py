"""
The models in this package use SQLAlchemy's object-relational mapping (ORM)
capabilities to acquire a persistent representation in a relational database
. The API makes use of these model classes to obtain a representation of a
resource in the database, as well as to describe the relations between
models. For example, a ``Service`` has a one-to-many relationship between
``Job``s, expressed by a ``FOREIGN KEY`` constraint in the relational database.

In order to create new database model classes, subclass
:class:`BASE`, found in the :mod:`.declarative_base`. Each persistent attribute
of a class must then map to a ``Column`` object provided by the database
schema. See the `SQLAlchemy documentation <https://goo.gl/bZD4Yd>`_
for more details about object-relational mapping.

.. note::

    If any database model classes will be inheriting from other model
    classes, SQLAlchemy will need to be notified. An inheritance model will
    need to be specified so that SQLAlchemy knows which class to instantiate
    for which database record. The `inheritance <https://goo.gl/naT59y>`_
    section in the SQLAlchemy documentation will give more data

"""
from .service import Service
from .job import Job, JobStatus
from .job_set import JobSet

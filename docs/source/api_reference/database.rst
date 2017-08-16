Database
========

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

Models
------

The models in this package use SQLAlchemy's object-relational mapping (ORM)
capabilities to acquire a persistent representation in a relational database
. The API makes use of these model classes to obtain a representation of a
resource in the database, as well as to describe the relations between
models. For example, a ``Service`` has a one-to-many relationship between
``Job``s, expressed by a ``FOREIGN KEY`` constraint in the relational database.

Abstract Database Model
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.database.models.abstract_database_model
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Service
~~~~~~~

.. automodule::  topchef.database.models.service
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Job
~~~

.. automodule:: topchef.database.models.job
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Job Set
~~~~~~~

.. automodule:: topchef.database.models.job_set
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__


Schemas
-------

The schema of a database is the set of all metadata that enables records to
be consistently entered into that database. By "consistent", what we mean is
 that any operation not resulting in an error maps the database from one
 valid state to another valid state. Unlike some no-SQL databases like
 MongoDB, relational databases require that a schema is defined before
 writing any records to the database. This module takes care of defining
 that schema, using abstractions provided by SQLAlchemy. Based on this
 schema and the particular database being used, SQLAlchemy can then generate
  the SQL code needed to perform a particular manipulation on a database model.

Abstract Database Schema
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.database.schemas.abstract_database_schema
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Database Schema
~~~~~~~~~~~~~~~

.. automodule:: topchef.database.schemas.database_schema
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Job Status
~~~~~~~~~~

.. automodule:: topchef.database.schemas.job_status
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

JSON Type
---------

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

.. automodule:: topchef.database.json_type
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

UUID Database Type
------------------

In a similar vein to the JSON column type, this type provides a back-end
agnostic way of storing Universally Unique Identifiers (UUIDs) in the
database. It will use the database's native UUID type if one exists. If not,
 the column will use a string type

.. automodule:: topchef.database.uuid_database_type
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__


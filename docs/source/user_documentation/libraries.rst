Libraries
=========

This document outlines some of the libraries used in this project. It
provides a brief overview of what they do, some caveats to watch out for
when using each library, and links to more documentation. This document is
meant for newcomers to the project to acquaint themselves with the project
dependencies

Installing
----------

As with most Python projects, the
`pip <https://pypi.python.org/pypi/pip>`_ package manager is used to manage
the dependencies between packages. ``pip`` takes care of installing Python
packages into one place, and resolving dependencies between python packages.
To install a library, run

.. sourcecode:: bash

    pip install $LIBRARY_NAME

where ``$LIBRARY_NAME`` is the name of the library to install. By default,
pip will pull its packages from `PyPI <https://pypi.python.org>`_. TopChef
has not been pushed to PyPI (yet). In order to install it, ``cd`` into the
top directory of this project and run

.. sourcecode:: bash

    pip install .

``pip`` will then take instructions from the ``setup.py`` module and install
 TopChef into the global ``site-packages`` directory. At that point, the
 ``topchef`` package will be accessible from any directory on the machine

Core Libraries
--------------

These libraries are listed in the ``setup.py`` module in the top of this
project. These libraries comprise the minimum set of libraries required to
run the server. Installing these libraries alone does not guarantee that all
the tests will be able to run.

Flask
~~~~~

Flask is a library for working with Python's
`Web Server Gateway Interface (WSGI) <https://goo.gl/6FhK5f>`_ in order to
process Hypertext Transfer Protocol (HTTP) requests. This project uses Flask
in order to map HTTP requests to Python functions. It also provides a set of
global variables like ``request``, which point to the current request that
the server is working on. Documentation for Flask is available
`here <http://flask.pocoo.org/docs/0.12/>`_. The
`pluggable view <http://flask.pocoo.org/docs/0.12/views/>`_ features of the
library were used in order to standardize logic for resource getting and
error reporting. These abstract endpoints are located in
:mod:`topchef.api.abstract_endpoints`.

JSONSchema
~~~~~~~~~~

The purpose of `jsonschema <https://pypi.python.org/pypi/jsonschema>`_ is to
take a JSON document and check that this document is compliant against a
JSON schema.

Marshmallow
~~~~~~~~~~~

`Marshmallow <https://marshmallow.readthedocs.io/en/latest/>`_ is a library
that can accept a Plain Old Python Object, and deserialize it into a Python
dictionary. The dictionary is determined by the properties of an object that
inherits from :class:`marshmallow.Schema`. Marshmallow can also go the other
way, taking in a dictionary, returning an object, and checking that the
input matches the schema. Unlike ``jsonschema``, ``marshmallow`` uses a
Python object instead of a JSON schema as the target schema.

Serializing user data in this way has several advantages. First, it provides
the codebase with a consistent way of accepting and checking user data. This
means that there is less of risk of incorrect or unexpected data being sent
into the API. Errors are easier to report as well, as they all come from one
serializer, and contain descriptions as to what went wrong. Getting these
features without Marshmallow would result in much more business logic

Marshmallow-JSONSchema
~~~~~~~~~~~~~~~~~~~~~~

`Marshmallow-JSONSchema <https://goo.gl/JbuVYL>`_ offers a means of writing
instances of :class:`marshmallow.Schema` as JSONSchema documents. This
library is used to display marshmallow schemas as JSON schema, in order to
allow client-side validation and API documentation.

SQLAlchemy
~~~~~~~~~~

`SQLAlchemy <https://goo.gl/bZD4Yd>`_ provides a layer of abstraction
between Python business logic and the relational databases that the API uses
for persistent storage. At its most abstract level, it provides an
`object-relational mapper (ORM) <https://goo.gl/8vjhnb>`_, that can map
instances of model classes to SQL Queries, turning each database record into
a Python object. SQLAlchemy also provides a :class:`sqlalchemy.Session` used
to stage the changes that a request intends to make into a single transaction.

As much as is feasible, each HTTP request should be mapped to a single
database transaction. This practice will allow for good error handling, as one
:class:`sqlalchemy.Session` can be associated with each request, and one
call to :meth:`sqlalchemy.Session.rollback` can undo all the database
changes in a request.

In addition to providing ORM capabilities, SQLAlchemy also provides objects
for interacting with tables and columns as Python objects, that SQLAlchemy
then maps into SQL code. This will be useful if we need to migrate lots of
data, or if one wishes to skip the overhead of creating Python objects from
the data in the database.

SQLAlchemy is also backend-agnostic, meaning that it can adapt to working
with different relational database products. This will prove useful if
TopChef ever needs to be scaled out.

Finally, SQLAlchemy provides a database ``engine`` that manages database
connections, reducing the overhead of repeatedly opening and closing
connections. The ``engine`` is also capable of distributing connections
between threads, ensuring that the state of connections remains consistent
across threads.

Flask-Script
~~~~~~~~~~~~

`Flask-Script <https://flask-script.readthedocs.io/en/latest/>`_ manages
writing scripts for server administration. An object provided by this
library is the first thing run when the server is started from the command
line. This library wraps Python's ``argparse`` library to parse command line
arguments.

If asked to run the server, this runner will use Flask's development server
to start the server. This is fine for development, but it is recommended to
use a dedicated web server to run TopChef in production.

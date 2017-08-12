Models
======

All resources in the API should be represented by a model class exported by
this package. The model classes in this package provide a layer of
abstraction between the models stored in the database, and the resources
that the user of this API will interact with. This package also provides
well-defined interfaces for working with resources, in order to describe a
contract for interacting the model classes. The contract in this case refers
to the set of properties and methods that an implementation of the contract
is guaranteed to implement. Unlike statically-typed languages like Java,
Python does not require such a contract to exist, as variable types can be
inferred dynamically. Nevertheless, it is recommended to use the
contracts defined here when making new implementations of model classes
for managing resources. Implementing these interfaces will also get the
most use out of the type-hinting syntax introduced in Python 3.4.

Interfaces
----------

API Error
~~~~~~~~~

.. automodule:: topchef.models.interfaces.api_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

API Metadata
~~~~~~~~~~~~

.. automodule:: topchef.models.interfaces.api_metadata
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Job
~~~

.. automodule:: topchef.models.interfaces.job
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Job List
~~~~~~~~

.. automodule:: topchef.models.interfaces.job_list
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Service
~~~~~~~

.. automodule:: topchef.models.interfaces.service
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Service List
~~~~~~~~~~~~

.. automodule:: topchef.models.interfaces.service_list
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__


Abstract Classes
----------------

These classes contain some often-repeated business logic.

API Error
~~~~~~~~~

.. automodule:: topchef.models.abstract_classes.api_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Job List From Query
~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.models.abstract_classes.job_list_from_query
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Errors
------

This package describes all reportable errors that the API may handle. Each
error type has an HTTP status code associated with it. API errors are also
throwable.

Deserialization Error
~~~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.models.errors.deserialization_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Method Not Allowed Error
~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.models.errors.method_not_allowed_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Not UUID Error
~~~~~~~~~~~~~~

.. automodule:: topchef.models.errors.not_uuid_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Serialization Error
~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.models.errors.serialization_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

Service Not Found Error
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: topchef.models.errors.service_not_found_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

SQLAlchemy Error
~~~~~~~~~~~~~~~~

.. automodule:: topchef.models.errors.sqlalchemy_error
    :members:
    :private-members:
    :special-members:
    :exclude-members: __dict__, __weakref__, __module__

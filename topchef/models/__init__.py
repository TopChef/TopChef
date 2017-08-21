"""
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

Model classes MUST keep track of the changes that they intend to make,
but they are not responsible for committing those changes. If the initial
state of a model class depends on some underlying representation like a
database record, changing the state of the class does not need to be
propagated immediately to persistent storage. In that case, propagation of
the state SHOULD go to a transaction manager that can then commit the
changes. If the state of a model class is modified, the modified value of
that attribute must be returned, even if that modified value was not yet
committed to storage.

In an effort to separate interface from implementation, each model class
defined here MUST expose its type and contract through an abstract base
class located in the ``interfaces`` directory of this package. Each class
imported into the ``__init__`` module of this package MUST be one of these
interfaces. 
"""
from .interfaces import Job
from .interfaces import JobList
from .interfaces import Service
from .interfaces import ServiceList
from .interfaces import APIMetadata
from .interfaces import APIError

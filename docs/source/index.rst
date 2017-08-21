.. TopChef documentation master file, created by
   sphinx-quickstart on Fri May  6 00:06:02 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TopChef's documentation!
===================================

TopChef solves the problem of getting a computer "here" to do something on a
computer over "there". It provides an abstraction layer over the networking,
so that the computer "here" doesn't need to known how to connect to the
computer "there", as long as it can connect to the TopChef server. It also
wraps all the logic behind an interface that runs through HTTP, so that
`any <http://docs.python-requests.org/en/master/>`_
`of <https://docs.oracle.com/javase/7/docs/api/java/net/package-summary.html>`_
`the <https://reference.wolfram.com/language/guide/WebOperations.html>`_
`multitude <http://cpp-netlib.org/#>`_
`of <https://www.mathworks.com/help/matlab/ref/webread.html>`_
`HTTP <https://hackage.haskell.org/package/http-client>`_
`clients <https://en.wikipedia.org/wiki/Ajax_(programming)>`_ out there can
work together to solve a problem. TopChef wants to make HTTP networking as
easy as making an HTTP request.

TopChef was originally developed at the Institute for Quantum Computing, in
order to enable online experiment design, connecting machine learning
algorithms to the control computers running experiments. To run TopChef, you
will need a server capable of connecting to both "here" and "there". The
recommended approach is to use the
`docker container <https://www.docker.com/what-container>`_. For more
information about installation and running the application, consult the
project's `README <https://github.com/TopChef/TopChef/blob/master/README.md>`_.

The project source code is hosted on
`GitHub <https://github.com/TopChef/TopChef>`_. Report bugs, feature
requests, support requests, and other issues to the project's
`issue tracker <https://github.com/TopChef/TopChef/issues>`_.

Features
--------

   * :ref:`json-schema` checks to make sure all messages are valid
   * Job result storage on
      - `MySQL <https://www.mysql.com/>`_
      - `PostgreSQL <https://www.postgresql.org/>`_
   * HTTP REST API for sending and receiving messages

HTTP API Guide
--------------

This section contains a detailed description of the HTTP endpoints exposed
by this application. For more details about about how HTTP works, see the
section :ref:`http-requests`.

.. qrefflask:: topchef:APP_FACTORY.app
   :undoc-static:

.. toctree::
   :maxdepth: 3

   http_api

The User Guide
--------------

This section contains tutorials on using the server, and on server
maintenance. It also provides introductory guides to some of the
technologies that TopChef needs to make it tick. If you want to know how to
do something in this server, or why some code was implemented in a
particular way, this is the section for you!

.. toctree::
   :maxdepth: 3

   user_documentation/index

API Reference
-------------

This section contains the nuts-and-bolts, nitty-gritty description of
TopChef. This section is composed primarily of auto-generated documentation
built from the source code that runs the server.

.. toctree::
   :maxdepth: 3

   api_reference/index

Overview
--------

The aim of this project is to have one TopChef server running per group,
providing a broker between multiple experiments and clients. To do this, we
need to consider the idea of a ``Service``, and a ``Job``.

A ``Service`` represents some entity that can listen for jobs, and that does
"one thing". Each ``Service`` has one :ref:`json-schema` for posting new
jobs, and one :ref:`json-schema` for posting results. These two schemas
specify the contract for the service.


A Practical Example:
~~~~~~~~~~~~~~~~~~~~

Suppose we want a service that adds one to a given integer. The JSON that
will create our service is given below. Let's assign this to a Python
variable for use later. All our HTTP requests will be done using Python's
:mod:`requests` library.

.. sourcecode:: python

   job_data = {
      "name": "Add One",
      "description": "Adds one to a given number",
      "job_registration_schema": {
         "title": "The schema for the service",
         "description": "Adds one to a given number",
         "$schema": "http://json-schema.org/schema#",
         "type": "object",
         "properties": {
            "value": {
               "title": "value",
               "description": "The number to add",
               "type": "integer"
            }
         },
         "required": ["value"]
      },
      "job_result_schema": {
         "title": "Results",
         "description": "The schema for valid job results",
         "$schema": "http://json-schema.org/schema#",
         "type": "object",
         "properties": {
            "result": {
               "title": "result",
               "description": "The result",
               "type": "integer"
            }
         },
         "required": ["value"]
      }
   }

This may look like a mouthful, but it is in fact quite simple. The ``name``
and ``description`` keys at the top level of the ``job_data`` variable
provide human-readable information to describe what our service will do. The
``job_registration_schema`` describes what the job parameters must look like.
In our case, the service will take an object that will have a key ``value``,
and the value of this key must be an integer. For instance, the object

.. sourcecode:: json

   {"value": 1}

is a valid parameter, but the object

.. sourcecode:: json

   {"value": "1"}

is not.

Let's say a ``TopChef`` server was already started, and is running on
address ``http://localhost:5000``. Using :mod:`requests`, the code to do
this will look something like

.. sourcecode:: python

   import requests
   import json

   url_to_post_to = 'http://localhost:5000/services'
   request_headers = {'Content-Type': 'application/json'}

   response = requests.post(
      url_to_post_to, headers=request_headers,
      json=job_data
   )
   assert response.status_code == 201

The ``assert`` statement at the bottom checks that the response returns the
status code ``201``, indicating that our service was successfully created.
As part of the process, TopChef will assign a universally-unique identifier
(UUID) to our service. Let's say that ID is
``66ca5284-ba62-4307-8739-4a09466a924f``.

In order to send jobs to this service, we can run code that looks something
like this

.. sourcecode:: python

   import requests
   import json

   data = {'parameters': {'value': '1'}}
   request_headers = {'Content-Type': 'application/json'}
   url_to_post_to =
      'http://localhost:5000/services/66ca5284-ba62-4307-8739-4a09466a924f/jobs`

   response = requests.post(
      url_to_post_to, headers=request_headers,
      data=data
   )
   assert response.status_code == 201

In a similar way to services, each ``Job`` also gets a job UUID. Let's say
that the job ID is ``d476cf16-356e-4828-bcb4-81c39f0c1aeb``.

If we were to send a ``GET`` request to
``/jobs/d476cf16-356e-4828-bcb4-81c39f0c1aeb``, we would find that the
request body looks like

.. sourcecode:: json

   {
      "id": "d476cf16-356e-4828-bcb4-81c39f0c1aeb",
      "status": "REGISTERED",
      "parameters": {
         "value": 1
      },
      "results": null
   }

We wait for the service to finish this job, and after some time, we get the
result

.. sourcecode:: json

   {
      "id": "d476cf16-356e-4828-bcb4-81c39f0c1aeb",
      "status": "COMPLETED",
      "parameters": {
         "value": 1
      },
      "results": {
         "result": 2
      }
   }

Our job is now complete.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _creating-a-service:

Creating A Service
==================

This document describes how to create a TopChef service that will do some
non-trivial task. To create this service, we will be using HTTP calls from
the :mod:`requests` library, although the recommended approach is to use
:mod:`topchef_client`, or a client written for your language.


The Service
-----------

Let's say that our service is just collecting a Free Induction Decay (FID)
on a sample. We will need to think ahead of time what such a service would
require, and eventually we settle on

* The length of time for which the pulse should be applied
* The number of data points to collect

We'll also consider the free induction decay signal as being an array of
integers, representing the intensity of the signal.

Creating the service will consist of

1. Writing down a :ref:`service-json-schema`
2. :ref:`checking-the-schema`
3. Posting the service to TopChef


Before we send any HTTP code, we'll go ahead and write down a
:ref:`json-schema` describing our parameters, and our results. To do this,
take a bottom-up approach to designing our schema.

.. _service-json-schema:

Service JSON Schema
~~~~~~~~~~~~~~~~~~~

The length of time for which the pulse is applied is a floating-point number
greater than 0. In JSON schema, we can write this down as

.. sourcecode:: json

    {
        "title": "Pulse Time",
        "description": "The length of time for which a pulse should be applied",
        "type": "number",
        "minimum": 0
    }

The ``title`` and ``description`` fields are there to let us humans know
what the parameter does. Use of these fields will let us make our schemas
more self-documenting and easier to understand.

.. sourcecode:: json

    {
        "title": "Data Points",
        "description": "The number of data points to collect",
        "type": "integer",
        "minimum": 0
    }

We'll say that the object to be sent encodes each of these points in keys
named ``pulse_time`` and ``data_points`` respectively. The JSON schema that
matches such an object is given below. Note that both properties are also
``required``. In keeping with good practice, we will also add a ``$schema``
key on the top level to let the world know what version of
:ref:`json-schema` we are using.

.. sourcecode:: json

    {
        "title": "Free Induction Decay",
        "description": "Describes a free induction decay experiment",
        "$schema": "http://json-schema.org/schema#",
        "type": "object",
        "properties": {
            "pulse_time": {
                "title": "Pulse Time",
                "description": "The length of time for which a pulse should be applied",
                "type": "number",
                "minimum": 0
            },
            "data_points": {
                "title": "Data Points",
                "description": "The number of data points to collect",
                "type": "integer",
                "minimum": 0
            }
        },
        "required": [
            "pulse_time",
            "data_points"
        ]
    }

We'll also write down a result :ref:`json-schema` as

.. sourcecode:: json

    {
        "title": "Free Induction Decay Results",
        "description": "The results for an FID",
        "$schema": "http://json-schema.org/schema#",
        "type": "array",
        "items": {
            "title": "FID entry",
            "description": "The entry into the FID result",
            "type": "object",
            "properties": {
                "time": {
                    "description": "The amount of time in seconds since the start of the FID experiment when this datum was collected",
                    "type": "number",
                    "minimum": 0
                },
                "intensity": {
                    "description": "The recorded intensity",
                    "type": "number"
                }
            }
        }
    }

.. _checking-the-schema:

Checking The Schema
~~~~~~~~~~~~~~~~~~~

Let's check that our result schema matches what we want to post. To do this,
we could use a :ref:`json-schema` validator built for the language that we
are working in, or the ``/validator`` endpoint provided by TopChef. The
following object will use TopChef's validator to check whether an instance
matches a schema. This code is Python 2 compliant.

.. sourcecode:: python

    import requests
    import json

    class Validator(object):
        """
        Checks an instance against a schema
        """
        def __init__(self, topchef_url):
            """
            :param str topchef_url: The URL for the base endpoint of TopChef
            """
            self._topchef_url = topchef_url

        def is_valid(instance, schema):
            """
            :param dict instance: The instance to check
            :param dict schema: The schema against which the instance is to
                be checked
            """
            data = {
                'schema': schema,
                'object': instance
            }
            response = requests.post(
                '%s/validator' % self._topchef_url,
                headers={'Content-Type': 'application/json'},
                json=data
            )
            return response.status_code == 200

The code above sends a ``POST`` request to the API's ``/validator``
endpoint, and checks whether the status code is ``200``. If it is, the
schema is valid

Posting The Service
~~~~~~~~~~~~~~~~~~~

Since we are satisfied with the service that we designed, let's go ahead and
 ``POST`` it to TopChef. To do this, we can run code similar to the listing
 below

.. sourcecode:: python

    import requests
    import json

    def create_service(
        topchef_url, service_name, service_description,
        registration_schema, result_schema):
        """
        :param str topchef_url: The URL to the topchef API
        :param str service_name: The name of the service
        :param str service_description: The service description
        :param dict registration_schema: The schema for making new jobs
        :param dict result_schema: The schema for posting results
        """
        data = {
            'name': service_name,
            'description': service_description,
            'job_registration_schema': registration_schema,
            'job_result_schema': result_schema
        }

        response = requests.post(
            '%s/services' % topchef_url,
            headers={'Content-Type': 'application/json'},
            json=data
        )

        assert response.status_code == 201

After we run this, we should see in our browsers that sending a ``GET``
request to ``/services`` will give us an entry with our service in it. We
only have to do this once for each service that we make.

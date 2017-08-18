JSON And JSON Schema
====================

`JavaScript Object Notation (JSON) <http://json.org/>`_
is a text format for exchanging object data between computers. It is a
subset of the JavaScript programming language that allows data structures to
be defined without containing executable JS code.

JSON defines strings, integers, floating-point numbers, booleans, and null
as primitive types. String must begin with and end with double quotes. A
boolean must be written as ``true`` or ``false``.

JSON also defines two composite data types; lists and objects. A list is an
ordered collection of elements. Each element in a list must be separated by
a comma. Elements of lists are allowed to be either primitive types or
composite types. In other words, lists of lists are allowed

Objects are unordered collections of key-value pairs. Only strings
are allowed to be keys. The value of this type can be either a primitive or
a composite type.

JSON is also whitespace-agnostic. Whitespace characters are syntactically
irrelevant to JSON parsers. In order to mark a new line in a string, the
newline character ``\n`` must be used.

An example of a JSON document is given below

.. sourcecode:: json

    {
        "key": "value",
        "number": 1,
        "boolean": true,
        "list_of_stuff": [
            "string",
            1,
            {
                "stuff": "more_stuff"
            }
        ]
    }

JSON Schema
-----------

`JSON Schema <http://json-schema.org/>`_ is a standard for creating JSON
objects that can describe other JSON objects, or sets of JSON objects.
TopChef uses JSON schema in order to describe valid jobs for a service, and
valid results that can be posted to finish a job. JSON schema accomplishes
this by using several keys to describe documents. The Space Telescope
Science Institute (`STSI <https://goo.gl/3g1P7h>`_) published a very useful
`guide <https://goo.gl/B8zhCR>`_ to understanding this format. The top-level
type of a JSON schema must be a JSON object.

The ``$schema`` key
~~~~~~~~~~~~~~~~~~~

``$schema`` is used to indicate whether a document is a JSON schema, and
which version of JSON schema it adheres to. If a JSON schema does not have a
``$schema`` keyword. It will be assumed that it adheres to the Draft 4
specification. This keyword can also be used to define a custom base schema
if there are any keywords that have been defined in schemas somewhere else.

Documentation Keys
~~~~~~~~~~~~~~~~~~

The ``title`` and ``description`` keys can be placed at any point in the
JSON schema. These keys are ignored while checking whether a JSON object
matches an instance. These keys are here so that the reader of a schema can
understand what is going on in the schema.

The ``type`` key
~~~~~~~~~~~~~~~~

``type`` determines which primitive or composite type this level of the
document must occupy. For instance, the most general JSON schema that can be
prepared is

.. sourcecode:: json

    {
        "$schema": "http://json-schema.org/schema#",
        "type": "object"
    }

The allowed values for ``type`` are

    * ``number``
    * ``integer``
    * ``boolean``
    * ``string``
    * ``object``
    * ``array``


Example: Nitrogen-Vacancy Center Experiment Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We've run our experiment, and we want to post three counts, a
``light_count``, ``dark_count``, and ``result_count``. All three of these
are integers, and they must be bigger than 0. All are required to post a
valid result set. A JSON schema for an object like this could look like

.. sourcecode:: json

    {
        "$schema": "http://json-schema.org/schema#",
        "title": "Nitrogen Vacancy Experiment Results",
        "description": "Describes a valid set of experiment results",
        "type": "object",
        "properties": {
            "light_count": {
                "title": "Light Count",
                "description": "The count taken from the light reference",
                "type": "integer",
                "minimum": 0
            },
            "dark_count": {
                "title": "Dark Count",
                "description": "The count taken from the dark reference",
                "type": "integer",
                "minimum": 0
            },
            "result_count": {
                "title": "Result Count",
                "description": "The count taken from the experiment sequence",
                "type": "integer",
                "minimum": 0
            }
        },
        "required": [
            "light_count",
            "dark_count",
            "result_count"
        ]
    }

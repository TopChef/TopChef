.. _http-requests:

Anatomy of an HTTP Request
==========================

This document provides an *ab initio* introduction to what HTTP is,
primarily to pin down definitions that will be used in more technical
documentation elsewhere in this project.

The Hypertext Transfer Protocol (HTTP) is a standard by which computers can
share hypertext with each other. Hypertext is text that may contain
references to other texts. The JavaScript Object Notation (JSON) format in
which messages are sent between clients and servers is an example of
hypertext, and so it is quite amenable to being sent by HTTP.

HTTP is a request-response protocol. This means that the party that requests
hypertext must be the party that initiates the request. The party that
requested the hypertext is called the client. The party that responds to the
request and presents the hypertext is called the server. The protocol does
not allow for the server presenting data without it being requested by the
client.

The Request
-----------

An HTTP request consists of

* A Uniform Resource Locator (URL)
* An HTTP Method
* A set of key-value pairs called HTTP headers
* An optional request body

The URL is an address that uniquely identifies the HTTP resource on which
the request should act. More often than not, a web site will have multiple
resources open for requests, meaning that the URL will also end up
describing the mechanism for retrieving these resources. This means that a
site like ``http://localhost:5000/`` can also have a resource at
``http://localhost:5000/services`` and at ``http://localhost:5000/jobs``.

The HTTP method is a string representing what the request intends to do to a
resource. The Internet Assigned Numbers Authority (IANA) maintains a
`list <https://goo.gl/cCSYmW>`_ of standard HTTP methods. One is free to
invent their own HTTP method, but they will also need to keep in mind that
most clients may not support it. Some HTTP methods like ``GET`` and ``HEAD``
are idempotent. This means that they MUST NOT modify the resource. Some
common methods are described below. This list should encompass all the HTTP
methods that this API uses. This list is not exhaustive.

+-------------+-------------+------------------------------------------+
|  Method     | Idempotent? | Action in this API                       |
+=============+=============+==========================================+
|  ``GET``    | Yes         | Retrieve a resource without modifying it |
+-------------+-------------+------------------------------------------+
| ``POST``    | No          | Create a new resource                    |
+-------------+-------------+------------------------------------------+
| ``PUT``     | No          | Modify a resource, with a full copy of   |
|             |             | the resource in the request body         |
+-------------+-------------+------------------------------------------+
| ``PATCH``   | No          | Modify a resource, with only the         |
|             |             | attributes of the resource to be         |
|             |             | modified being in the request body       |
+-------------+-------------+------------------------------------------+
| ``DELETE``  | No          | Delete the resource                      |
+-------------+-------------+------------------------------------------+
| ``HEAD``    | Yes         | Retrieve the headers that will be        |
|             |             | returned for a GET request to the        |
|             |             | resource, without the resource body      |
+-------------+-------------+------------------------------------------+
| ``OPTIONS`` | Yes         | Describes the communication protocol     |
|             |             | for a resource. This may include         |
|             |             |                                          |
|             |             | * The allowed HTTP methods               |
|             |             | * The allowed content types              |
|             |             | * The allowed sources that can request   |
|             |             |   the resource                           |
+-------------+-------------+------------------------------------------+

The HTTP headers are a set of strings organized into key-value pairs. The
purpose of HTTP headers is to communicate request metadata. For example, if
a resource requires authentication to access, the authentication credentials
may be written as the value of the ``Authorization`` key. Two important
headers for this API are ``Content-Type`` and ``X-HTTP-METHOD-OVERRIDE``.
HTTP headers are case-insensitive, so ``Content-Type`` is the same thing as
``CoNtEnT-TyPe``. If a request body is provided, the ``Content-Type`` header
indicates the format used to encode the request body. As of now, the only
value allowed for requests is ``application/json``. This header must also be
supplied in idempotent methods in order to indicate the format in which the
response is desired. The process of determining which format the server
should send data is called `content negotation <https://goo.gl/dTDTZp>`_.
The ``X-HTTP-METHOD-OVERRIDE`` header is used to override the HTTP method.
If it is present, the server will treat the request as having the method
defined as the value of this key. This is present for compatibility reasons,
in case an HTTP client does not support requests of a given method. This has
been a problem when using the ``java.net.URL`` library for TopChef's
`Java client <https://github.com/TopChef/JavaClient>`_ when implementing
``PATCH`` requests.

Finally, the HTTP body is a string of text that contains the data to be sent
with either a request or a response. Not all requests and responses need to
have a body. In the case of a ``GET`` request, the body may contain the HTML
code that a browser needs to render a website. In the case of this API, the
request bodies will contain a JSON document representing the resource data

The Response
------------

As well as defining a standard for requests, HTTP defines a standard for
responses. An HTTP response consists of

* A status line
* The response headers
* An optional response body

The status line has the form ``HTTP-<version> SP <status-code> SP
<reason-phrase> CRLF``. ``<version>`` represents the version of HTTP in
which the response is encoded. The ``<status code>`` is a three-digit
integer that describes the request status. The HTTP standard defines a
meaning for the hundreds digit of the status code from ``1XX`` to ``5XX``.
It also defines a common set of status codes. Some of the status codes
encountered in this API, along with their meaning, are given below. See the
HTTP API documentation for more details about what codes each endpoint returns.

+----------+---------------------------+
| Code     | Status Phrase             |
+----------+---------------------------+
|  ``200`` | ``OK``                    |
+----------+---------------------------+
|  ``201`` | ``CREATED``               |
+----------+---------------------------+
|  ``204`` | ``NO CONTENT``            |
+----------+---------------------------+
|  ``304`` | ``NOT MODIFIED``          |
+----------+---------------------------+
|  ``400`` | ``BAD REQUEST``           |
+----------+---------------------------+
|  ``404`` | ``NOT FOUND``             |
+----------+---------------------------+
|  ``405`` | ``METHOD NOT ALLOWED``    |
+----------+---------------------------+
|  ``500`` | ``INTERNAL SERVER ERROR`` |
+----------+---------------------------+

The response headers fulfill the same function as the request headers,
communicating metadata about the response. The response will include a
``Content-Type`` header to indicate the format of the response body.

The response body contains the desired data.

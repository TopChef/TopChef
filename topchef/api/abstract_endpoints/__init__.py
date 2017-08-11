"""
Contains abstract classes that manage much of the repeated business logic
when it comes to fetching resources across multiple endpoints. These classes
also modify their subclasses at import time so that web-enabled methods can
take the resources they work on as their arguments.

For instance, an endpoint that maps ``/services/<service_id>`` will pretty
much always need to get a ``Service`` with an ID matching ``serviceID``. If
it didn't, then there would be no point asking for the ID in the API. Flask
will take the ``service_id`` from the endpoint, and then pass it in as an
argument to a method that Flask dispatches. Using the classes defined here,
we can define these methods (like ``get``) to work with ``Service`` instead
of ``service_id``. The error handling is done once, in a separate place.
"""
from .abstract_endpoint import AbstractEndpoint
from .endpoint_for_service import AbstractEndpointForServiceMeta
from .endpoint_for_service import AbstractEndpointForService
from .endpoint_for_service import EndpointForServiceIdMeta

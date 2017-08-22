"""
:mod:`marshmallow` and :mod:`marshmallow_jsonschema` sometimes interact
in ways that require custom fields. These fields treat variables in a way
that is not provided in standard :mod:`marshmallow.fields`. For instance,
the ``JobStatusField`` needs to be here in order to correctly serialize and
deserialize enums of type :class:`topchef.models.Job.JobStatus`. It also needs
to present these enumerations in an "enum" key in JSON schema, as this is
the means by which JSON schema encodes enumerations.
"""
from .job_status_field import JobStatusField

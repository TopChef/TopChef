"""
Contains a serializer for rough serialization of jobs
"""
from marshmallow import Schema, fields
from topchef.models import Job


class _JobStatusField(fields.Field):
    """
    Describes a field that can be used to serialize an enum of type
    ``JobStatus``
    """
    def _serialize(self, value: Job.JobStatus, attr, obj: Job) -> str:
        """
        Overwrite the ``_serialize`` method in Marshmallow to describe how
        to take the complicated type and turn it into a more native python
        data type

        :param value: The value to be serialized
        :param attr: The attribute or key on the object to be serialized
        :param obj: The object that the value was pulled from
        :return: The serialized field
        """
        if value is Job.JobStatus.REGISTERED:
            status = "REGISTERED"
        elif value is Job.JobStatus.WORKING:
            status = "WORKING"
        elif value is Job.JobStatus.COMPLETED:
            status = "COMPLETED"
        elif value is Job.JobStatus.ERROR:
            status = "ERROR"
        else:
            raise ValueError(
                'Attempted to serialize a value %s for which a value is not '
                'defined'
            )
        return status

    def _deserialize(self, value: str, attr, data: dict) -> Job.JobStatus:
        value_to_check = value.upper()
        if value_to_check == "REGISTERED":
            status = Job.JobStatus.REGISTERED
        elif value_to_check == "WORKING":
            status = Job.JobStatus.WORKING
        elif value_to_check == "COMPLETED":
            status = Job.JobStatus.COMPLETED
        elif value_to_check == "ERROR":
            status = Job.JobStatus.ERROR
        else:
            raise ValueError(
                'Unknown value for enum'
            )
        return status

    def _jsonschema_type_mapping(self) -> dict:
        """

        :return: How the field is to be expressed in JSON Schema
        """
        return {
            'type': 'string',
            'enum': ['REGISTERED', 'WORKING', 'COMPLETED', 'ERROR']
        }


class JobOverview(Schema):
    """
    Describes an overview schema for serializing general information about jobs
    """
    id = fields.UUID(dump_only=True, required=True)
    status = _JobStatusField(dump_only=True, required=True)
    date_submitted = fields.DateTime(dump_only=True, required=True)

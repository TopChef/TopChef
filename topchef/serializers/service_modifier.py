"""
Contains a serializer for modifying the service
"""
from datetime import timedelta
from marshmallow import Schema, fields, validates, ValidationError


class ServiceModification(Schema):
    is_available = fields.Boolean(required=False)
    description = fields.Str(required=False)
    name = fields.Str(required=False)
    timeout = fields.TimeDelta(required=False)

    @validates('timeout')
    def validate_timeout(self, timeout: timedelta):
        if timeout.total_seconds() < 0:
            raise ValidationError(
                'Attempted to set a negative timeout duration'
            )
        else:
            return True

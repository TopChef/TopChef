"""
Describes how to serialize the models in :mod:`models.py` to JSON objects
"""
from rest_framework.serializers import ModelSerializer
from .models import Service, Job


class ServiceSerializer(ModelSerializer):
    """
    Takes a :class:`models.Service` and dumps it to the required
    representations
    """
    class Meta(object):
        """
        Describes the metadata for the serializer
        """
        model = Service
        fields = {
            'id', 
            'name', 
            'description', 
            'job_registration_schema', 
            'job_result_schema'
        }


class JobSerializer(ModelSerializer):
    """
    Serializes :class:`Job`
    """
    class Meta(object):
        """
        Describes metadata for the serializer
        """
        model = Job
        fields = {
            'id',
            'parameters',
            'result',
            'status'
        }


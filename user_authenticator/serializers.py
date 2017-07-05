"""
Contains models responsible for taking in Python objects and marshalling them
to the API
"""
from django.contrib.auth.models import  User, Group
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """
    Responsible for serializing Users
    """
    class Meta(object):
        """
        Represents metadata for this serializer
        """
        model = User
        fields = {'url', 'username', 'email', 'groups'}

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    """
    Responsible for serializing groups.
    """
    class Meta(object):
        """
        Represents metadata for this serializer
        """
        model = Group
        fields = {'url', 'name'}


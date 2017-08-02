"""
Contains the Flask blueprint for the API
"""
from .api_metadata import APIMetadata
from flask_restful import Api

api = Api()
api.add_resource(APIMetadata, '/')

"""
Describes an endpoint where detailed information about the service can be
obtained
"""
from flask import Response, jsonify
from topchef.api.abstract_endpoints import AbstractEndpointForService
from topchef.api.abstract_endpoints import AbstractEndpointForServiceMeta
from topchef.models import Service
from topchef.serializers import JSONSchema
from topchef.serializers import ServiceDetail as ServiceSerializer


class ServiceDetail(AbstractEndpointForService):
    """
    Describes the endpoint that returns the details for a particular service
    """
    def get(self, service: Service) -> Response:
        """

        :param service: The service for which a response is to be retrieved
        :return: A flask response with the appropriate data
        """
        serializer = ServiceSerializer()
        serializer_schema = JSONSchema(
            title='Detailed Service Schema',
            description='A comprehensive schema for displaying services'
        )
        response = jsonify({
            'data': serializer.dump(service, many=False).data,
            'meta': {'service_schema': serializer_schema.dump(serializer)},
            'links': {'self': self.self_url(service)}
        })
        response.status_code = 200
        return response


class ServiceDetailForServiceID(
    ServiceDetail, metaclass=AbstractEndpointForServiceMeta
):
    """
    Contains a mixin to help the web endpoints parse ``service_id`` string
    as they come raw from the HTTP endpoint
    """

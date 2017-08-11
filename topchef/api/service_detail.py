"""
Describes an endpoint where detailed information about the service can be
obtained
"""
from typing import Optional
from uuid import UUID

from flask import Response, jsonify, Request, request
from sqlalchemy.orm import Session

from topchef.api.abstract_endpoints import AbstractEndpointWithService
from topchef.models import Service, ServiceList
from topchef.serializers import JSONSchema
from topchef.serializers import ServiceDetail as ServiceSerializer


class ServiceDetail(AbstractEndpointWithService):
    """
    Describes the endpoint that returns the details for a particular service
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            service_list_model: Optional[ServiceList]=None
    ) -> None:
        """
        Create the service list model

        :param session: The database session to use for making the request
        """
        super(self.__class__, self).__init__(
            session, request=flask_request, service_list=service_list_model
        )

    def get(self, service: Service) -> Response:
        """

        :param service: The service for which a response is to be retrieved
        :return:
        """
        serializer = ServiceSerializer()
        serializer_schema = JSONSchema(
            title='Detailed Service Schema',
            description='A comprehensive schema for displaying services'
        )
        response = jsonify({
            'data': serializer.dump(service, many=False).data,
            'meta': {'service_schema': serializer_schema.dump(serializer)},
            'links': self.links
        })
        response.status_code = 200
        return response

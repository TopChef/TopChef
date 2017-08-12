"""
Describes the endpoint for listing services
"""
from flask import jsonify, Response, request, Request
from sqlalchemy.orm import Session
from typing import Optional
from topchef.api.abstract_endpoints.abstract_endpoint import AbstractEndpoint
from topchef.models import ServiceList as ServiceListInterface
from topchef.models.errors import DeserializationError, SerializationError
from topchef.models.service_list import ServiceList as ServiceListModel
from topchef.serializers import JSONSchema
from topchef.serializers import NewService as NewServiceSerializer
from topchef.serializers import ServiceOverview as ServiceOverviewSerializer


class ServicesList(AbstractEndpoint):
    """
    Maps methods for listing services as well as creating a service
    """
    def __init__(
            self, session: Session,
            flask_request: Request=request,
            service_list: Optional[ServiceListInterface]=None
    ) -> None:
        """

        Create a service list model that is capable of getting services from
        the DB

        :param session: The database session to use
        """
        super(self.__class__, self).__init__(session, flask_request)

        if service_list is not None:
            self.service_list = service_list
        else:
            self.service_list = ServiceListModel(session)

    def get(self) -> Response:
        """
        Returns a list of all services exposed by this API

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json



        :return: A Flask response with the appropriate data
        """
        response = jsonify({
            'data': self._data, 'meta': self._meta, 'links':
            self.links
        })
        response.status_code = 200
        return response

    def post(self) -> Response:
        """

        :return: A flask response indicating whether creation of the service
            was successful or not
        """
        serializer = NewServiceSerializer(strict=True, many=False)
        data, errors = serializer.load(request.json)

        if errors:
            self._report_client_serialization_errors(errors)
            raise self.Abort()
        else:
            response = self._make_service_from_data(data)

        return response

    @property
    def _data(self) -> dict:
        """

        :return: The JSON corresponding to all the services loaded onto the
            API
        """
        serializer = ServiceOverviewSerializer()
        service_list, errors = serializer.dump(self.service_list, many=True)

        if errors:
            self._report_server_serialization_errors(errors)
            raise self.Abort()

        return service_list

    @property
    def _meta(self) -> dict:
        """

        :return: The endpoint metadata
        """
        service_schema = JSONSchema(
            title='Service overview schema',
            description='The schema for each entry in the services list'
        )
        new_service_schema = JSONSchema(
            title='New Service Schema',
            description='The schema that must be satisfied in order to post '
                        'a new service'
        )
        return {
            'service_schema': service_schema.dump(ServiceOverviewSerializer()),
            'new_service_schema': new_service_schema.dump(
                NewServiceSerializer()
            )
        }

    def _report_client_serialization_errors(self, errors: list) -> None:
        self.errors.extend(DeserializationError(error) for error in errors)

    def _report_server_serialization_errors(self, errors: list) -> None:
        self.errors.extend(SerializationError(error) for error in errors)

    def _make_service_from_data(self, data) -> Response:
        self.service_list.new(
            data['name'],
            data['description'],
            data['job_registration_schema'],
            data['job_result_schema']
        )
        return self._make_correct_response()

    def _make_correct_response(self) -> Response:
        response = jsonify({
            'data': {'message': 'service successfully created'},
            'links': self.links
        })
        response.status_code = 201
        return response

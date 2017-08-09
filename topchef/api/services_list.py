"""
Describes the endpoint for listing services
"""
from .abstract_endpoint import AbstractEndpoint
from flask import jsonify, Response, request
from topchef.models import ServiceList as ServiceListInterface
from topchef.models.service_list import ServiceList as ServiceListModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from topchef.models.exceptions import DeserializationError, SerializationError
from topchef.serializers import JSONSchema
from topchef.serializers import ServiceOverview as ServiceOverviewSerializer
from topchef.serializers import NewService as NewServiceSerializer
from typing import Type


class ServicesList(AbstractEndpoint):
    """
    Maps methods for listing services as well as creating a service
    """
    def __init__(
            self, session: Session,
            service_list_model: Type[ServiceListInterface]=ServiceListModel
    ) -> None:
        """

        Create a service list model that is capable of getting services from
        the DB

        :param session: The database session to use
        """
        super(self.__class__, self).__init__(session)
        self.service_list = service_list_model(self.database_session)

    def get(self) -> Response:
        """

        :return A Flask response with the appropriate data
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

    @property
    def _error_schema(self) -> dict:
        """

        :return: The schema for marshmallow serialization errors
        """
        return {
            '$schema': "http://json-schema.org/schema#",
            'title': 'Serialization Error Schema',
            'description': 'The schema for errors in the errors key of this '
                           'response',
            'type': 'array',
            'items': {
                'type': 'string'
            }
        }

    def _make_service_from_data(self, data) -> Response:
        self.service_list.new(
            data['name'],
            data['description'],
            data['job_registration_schema'],
            data['job_result_schema']
        )

        try:
            self.database_session.commit()
        except SQLAlchemyError as error:
            self.database_session.rollback()
            return self._make_commit_error(error)
        else:
            return self._make_correct_response()

    def _make_commit_error(self, error: SQLAlchemyError) -> Response:
        response = jsonify({
            'errors': [str(error)],
            'meta': self._error_schema,
            'links': self.links
        })
        response.status_code = 500
        return response

    def _make_correct_response(self) -> Response:
        response = jsonify({
            'data': {'message': 'service successfully created'},
            'links': self.links
        })
        response.status_code = 201
        return response

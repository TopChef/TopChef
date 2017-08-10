"""
Describes the root endpoint of the API, which provides some metadata about
the API.
"""
from .abstract_endpoint import AbstractEndpoint
from flask import jsonify, Response, Request, request
from topchef.serializers import APIMetadata as MetadataSerializer
from topchef.serializers import JSONSchema
from topchef.models import APIMetadata as APIMetadataModelInterface
from topchef.models.api_metadata import APIMetadata as MetadataModel
from sqlalchemy.orm import Session


class APIMetadata(AbstractEndpoint):
    """
    Maps HTTP ``GET`` methods to the API's root endpoint
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            metadata: APIMetadataModelInterface=MetadataModel()
    ) -> None:
        """

        :param session: The SQLAlchemy ORM Session to use for communicating
            with the database. This is required by ``AbstractEndpoint`` in
            order to perform its transaction management
        :param flask_request: The request to process. By default, this is
            flask's ``request`` variable
        :param metadata: The metadata to serialize. By default, this is an
            instance of the ``MetadataModel`` that pulls all of its values
            from the ``config`` script.
        """
        super(APIMetadata, self).__init__(session, request=flask_request)
        self._api_metadata = metadata

    def get(self) -> Response:
        """

        :return: A response containing the metadata
        """
        response = jsonify({
            'data': self._data, 'meta': self._meta, 'links': self.links
        })
        response.status_code = 200
        return response

    @property
    def _data(self) -> dict:
        serializer = MetadataSerializer(strict=True)
        return serializer.dump(self._api_metadata, many=False).data

    @property
    def _meta(self) -> dict:
        serializer = MetadataSerializer(strict=True)
        json_schema_serializer = JSONSchema(
            title=self.metadata_schema_title,
            description=self.metadata_schema_description
        )
        return {
            'schema': json_schema_serializer.dump(serializer, many=False)
        }

    @property
    def metadata_schema_title(self) -> str:
        return 'API Metadata'

    @property
    def metadata_schema_description(self) -> str:
        return 'Describes the JSON schema for describing API metadata'

"""
Describes an API endpoint that describes the endpoint for ``/jobs``
"""
from topchef.models.job_list import JobList as JobListModel
from .abstract_endpoint import AbstractEndpoint
from sqlalchemy.orm import Session
from flask import Response
from flask import jsonify
from topchef.serializers import JobOverview as JobSerializer
from topchef.serializers import JSONSchema


class JobsList(AbstractEndpoint):
    """
    Maps HTTP requests for the ``/jobs`` endpoint to methods in this class
    """
    def __init__(self, session: Session) -> None:
        """

        :param session: The session to use
        """
        super(self.__class__, self).__init__(session)
        self.job_list = JobListModel(self.database_session)

    def get(self) -> Response:
        """

        :return: The list of all jobs on the system
        """
        response = jsonify({
            'data': self._data, 'meta': self._meta, 'links': self.links
        })
        response.status_code = 200
        return response

    @property
    def _data(self) -> dict:
        """

        :return: The JSON containing a list of all the jobs on the system
        """
        serializer = JobSerializer()
        return serializer.dump(self.job_list, many=True)

    @property
    def _meta(self) -> dict:
        return {
            'data_schema': self._data_schema
        }

    @property
    def _data_schema(self) -> dict:
        """

        :return:
        """
        json_serializer = JSONSchema()

        return {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'Job Endpoint Schema',
            'description': 'Describes how jobs are presented in the "data" '
                           'endpoint',
            'type': 'array',
            'items': json_serializer.dump(JobSerializer())
        }

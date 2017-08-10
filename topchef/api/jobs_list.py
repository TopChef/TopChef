# -*- coding: utf-8 -*-
"""
Describes an API endpoint that describes the endpoint for ``/jobs``
"""
from topchef.models import JobList as JobListInterface
from topchef.models.job_list import JobList as JobListModel
from .abstract_endpoint import AbstractEndpoint
from sqlalchemy.orm import Session
from flask import Request, Response
from flask import request, jsonify
from topchef.serializers import JobOverview as JobSerializer
from topchef.serializers import JSONSchema
from typing import Optional

__all__ = ["JobsList"]


class JobsList(AbstractEndpoint):
    """
    Maps HTTP requests for the ``/jobs`` endpoint to methods in this class
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            job_list_model: Optional[JobListInterface]=None
    ) -> None:
        """

        :param session: The session to use
        :param flask_request: The Flask request that this endpoint needs to
            process
        """
        super(self.__class__, self).__init__(session, flask_request)
        if job_list_model is None:
            self.job_list = JobListModel(self.database_session)
        else:
            self.job_list = job_list_model

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
        return serializer.dump(self.job_list, many=True).data

    @property
    def _meta(self) -> dict:
        return {
            'data_schema': self._data_schema
        }

    @property
    def _data_schema(self) -> dict:
        """

        :return: A JSON schema for the data in the ``data`` key of this
            response
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

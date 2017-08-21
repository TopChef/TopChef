# -*- coding: utf-8 -*-
"""
Describes an API endpoint that describes the endpoint for ``/jobs``
"""
from typing import Optional

from flask import Request, Response
from flask import request, jsonify
from sqlalchemy.orm import Session

from topchef.api.abstract_endpoints.abstract_endpoint import AbstractEndpoint
from topchef.models import JobList as JobListInterface
from topchef.models.job_list import JobList as JobListModel
from topchef.serializers import JSONSchema
from topchef.serializers import JobOverview as JobSerializer

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
        r"""
        Get the list of all jobs on the system

        .. :quickref: Job List; Get all the jobs in the API

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-Type: application/json

            {
                "data": [
                    {
                      "date_submitted": "2017-08-15T18:29:07.902093+00:00",
                      "id": "42094fe4-9c71-4d6e-94fd-7ed6e2b46ce7",
                      "status": "REGISTERED"
                    }
                ],
                "links": {
                    "self": "http://127.0.0.1:5000/jobs"
                },
                "meta": {
                    "data_schema": {
                        "$schema": "http://json-schema.org/draft-04/schema#",
                        "description": "Describes how jobs are presented in the \"data\" endpoint",
                        "items": {
                            "$schema": "http://json-schema.org/draft-04/schema#",
                            "properties": {
                            "date_submitted": {
                                "format": "date-time",
                                "readonly": true,
                                "title": "date_submitted",
                                "type": "string"
                            },
                            "id": {
                                "format": "uuid",
                                "readonly": true,
                                "title": "id",
                                "type": "string"
                            },
                            "status": {
                                "enum": [
                                    "REGISTERED",
                                    "WORKING",
                                    "COMPLETED",
                                    "ERROR"
                                ],
                                "type": "string"
                                }
                            },
                            "required": [
                              "date_submitted",
                              "id",
                              "status"
                            ],
                            "type": "object"
                        },
                        "title": "Job Endpoint Schema",
                        "type": "array"
                    }
                }
            }

        :statuscode 200: The request completed successfully

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

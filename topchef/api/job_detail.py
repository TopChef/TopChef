"""
Maps the ``jobs/<job_id>`` endpoint
"""
from jsonschema import Draft4Validator as JsonschemaValidator
from jsonschema import ValidationError as JsonSchemaValidatorError
from sqlalchemy.orm import Session
from flask import Response, jsonify, url_for, Request, request
from topchef.models import Job, JobList
from topchef.models.errors import ValidationError
from topchef.api.abstract_endpoints import AbstractEndpointForJob
from topchef.api.abstract_endpoints import AbstractEndpointForJobMeta
from topchef.serializers import JSONSchema
from topchef.serializers import JobDetail as JobSerializer
from topchef.serializers import JobModification as JobModificationSerializer
from topchef.models.errors import DeserializationError
from typing import Dict, Optional, Type, Iterable
from uuid import UUID


class JobDetail(AbstractEndpointForJob):
    """
    Contains details for a particular job
    """
    def __init__(
            self,
            session: Session,
            flask_request: Request=request,
            job_list:Optional[JobList]=None,
            validator_factory: Type[JsonschemaValidator]=JsonschemaValidator
    ) -> None:
        super(JobDetail, self).__init__(
            session, flask_request, job_list
        )
        self._validator_factory = validator_factory

    def get(self, job: Job) -> Response:
        """

        :param job: The job for which a response is to be obtained
        :return:
        """
        serializer = JobSerializer()
        serializer_schema = JSONSchema(
            title='Detailed Job Schema',
            description='The schema for all displayable data for a job'
        )
        job_modification_serializer = JobModificationSerializer()
        response = jsonify({
            'data': serializer.dump(job, many=False).data,
            'meta': {
                'job_info_schema': serializer_schema.dump(serializer),
                'patch_request_schema': serializer_schema.dump(
                    job_modification_serializer
                )
            },
            'links': {
                'self': self._self_url(job.id)
            }
        })
        response.status_code = 200
        return response

    def patch(self, job: Job) -> Response:
        """

        :param job: The job to be modified
        :return: The response
        """
        serializer = JobModificationSerializer()
        job_reporting_serializer = JobSerializer()

        data, errors = serializer.load(self.request_json)

        if errors:
            self._report_loading_errors(errors)
            raise self.Abort()

        if 'results' in data.keys():
            self._modify_job_results(job, data['results'])

        if 'status' in data.keys():
            self._modify_job_status(job, data['status'])

        response = jsonify(job_reporting_serializer.dump(job).data)
        response.status_code = 200
        return response

    def _report_loading_errors(self, errors: Dict[str, str]) -> None:
        self.errors.extend(
            DeserializationError(key, errors[key]) for key in errors.keys()
        )

    def _report_validation_errors(
            self, errors: Iterable[JsonSchemaValidatorError]
    ) -> None:
        self.errors.extend(
            ValidationError(error) for error in errors
        )

    def _self_url(self, job_id: UUID) -> str:
        """

        :param job_id: The ID of the job for which the endpoint has been found
        :return: The URL for the endpoint that was accessed by the user
        """
        return url_for(self.__class__.__name__, job_id=str(job_id),
                       _external=True)

    def _modify_job_results(self, job: Job, results: dict) -> None:
        json_schema_validator = self._validator_factory(job.result_schema)

        if not json_schema_validator.is_valid(results):
            self._report_validation_errors(
                json_schema_validator.iter_errors(results)
            )
            raise self.Abort()
        else:
            job.results = results

    @staticmethod
    def _modify_job_status(job: Job, status: Job.JobStatus) -> None:
        job.status = status


class JobDetailForJobID(
    JobDetail, metaclass=AbstractEndpointForJobMeta
):
    """
    Contains a mixin to map a job UUID to a job endpoint
    """

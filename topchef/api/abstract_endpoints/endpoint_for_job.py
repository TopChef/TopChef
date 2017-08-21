"""
Describes an abstract endpoint that maps a Job UUID to a particular Job
"""
import abc
from .abstract_endpoint import AbstractMethodViewType
from uuid import UUID
from functools import wraps
from flask import Response, Request, request
from typing import Union, Optional
from topchef.api.abstract_endpoints import AbstractEndpoint
from topchef.models.errors import NotUUIDError, JobWithUUIDNotFound
from topchef.models import Job, JobList
from topchef.models.job_list import JobList as JobListModel
from sqlalchemy.orm import Session


class EndpointForJobIdMeta(AbstractMethodViewType):
    """
    A metaclass that describes how to get the job for a particular Job UUID
    """
    def __init__(cls, name, bases, namespace) -> None:
        super(EndpointForJobIdMeta, cls).__init__(name, bases, namespace)

        for base in bases:
            if hasattr(base, 'job_list'):
                namespace['job_list'] = base.job_list

        if 'job_list' not in namespace.keys():
            raise ValueError(
                'Unable to create the job list. '
                'The class must have a property called "job_list"'
            )
        else:
            cls.job_list = namespace['job_list']

        cls._decorate_endpoints()

    def _job_decorator(cls, function_to_decorate):
        """

        :param function_to_decorate: The job endpoint to decorate
        :return:
        """

        @wraps(function_to_decorate)
        def decorated_function(
                instance, job_id: str, *args, **kwargs
        ) -> Response:
            if not cls._is_uuid(job_id):
                raise NotUUIDError(job_id)

            job = cls._get_job(instance, UUID(job_id))

            return function_to_decorate(instance, job, *args, **kwargs)

        return decorated_function

    @staticmethod
    def _is_uuid(job_id: Union[str, UUID]) -> bool:
        if isinstance(job_id, UUID):
            return True
        try:
            UUID(job_id)
            return True
        except ValueError:
            return False

    @staticmethod
    def _get_job(instance, job_id: UUID) -> Job:
        try:
            return instance.job_list[job_id]
        except KeyError:
            raise JobWithUUIDNotFound(job_id)

    def _decorate_endpoints(cls) -> None:
        if hasattr(cls, 'get'):
            cls.get = cls._job_decorator(cls.get)
        if hasattr(cls, 'put'):
            cls.put = cls._job_decorator(cls.put)
        if hasattr(cls, 'post'):
            cls.post = cls._job_decorator(cls.post)
        if hasattr(cls, 'patch'):
            cls.patch = cls._job_decorator(cls.patch)
        if hasattr(cls, 'delete'):
            cls.delete = cls._job_decorator(cls.delete)


class AbstractEndpointForJobMeta(EndpointForJobIdMeta, abc.ABCMeta):
    pass


class AbstractEndpointForJob(AbstractEndpoint, metaclass=abc.ABCMeta):
    def __init__(
            self, session: Session, flask_request: Request=request,
            job_list: Optional[JobList]=None
    ):
        super(AbstractEndpointForJob, self).__init__(session, flask_request)
        if job_list is None:
            self._job_list = JobListModel(self.database_session)

    @property
    def job_list(self) -> JobList:
        return self._job_list

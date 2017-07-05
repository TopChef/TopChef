"""
Describes model classes for the TopChef API.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class Service(models.Model):
    """
    Describes a service. A service is a resource capable of launching jobs.
    """
    id = models.UUIDField(
            primary_key=True, default=uuid.uuid4, editable=False
    )
    name = models.TextField()
    description = models.TextField()
    last_checked_in = models.DateTimeField()
    heartbeat_timeout = models.IntegerField()
    maintainer = models.ForeignKey(User, on_delete=models.CASCADE)
    job_registration_schema = models.FileField()
    job_result_schema = models.FileField()


class Job(models.Model):
    """
    Describes a job. A job contains one set of parameters, and one set
    of results. The parameters and results match the job registration schema,
    and the job result schema for the parent service, respectively.
    """

    JOB_STATUS_CHOICES = [
        ("REGISTERED", "REGISTERED"),
        ("WORKING", "WORKING"),
        ("COMPLETED", "COMPLETED")
    ]

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    parameters = models.FileField()
    result = models.FileField(null=True)
    status = models.CharField(
            choices=JOB_STATUS_CHOICES, default="REGISTERED",
            max_length=20
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)


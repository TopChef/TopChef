"""
Contians the presentation layer for the TopChef API
"""
from rest_framework.viewsets import ModelViewSet
from .models import Service, Job
from .serializers import ServiceSerializer, JobSerializer

class ServiceViewSet(ModelViewSet):
    """
    Presents services
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class JobViewSet(ModelViewSet):
    """
    Responsible for presenting jobs
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    

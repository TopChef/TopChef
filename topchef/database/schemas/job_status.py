from enum import Enum


class JobStatus(Enum):
    REGISTERED = "REGISTERED"
    COMPLETED = "COMPLETED"
    WORKING = "WORKING"
    ERROR = "ERROR"

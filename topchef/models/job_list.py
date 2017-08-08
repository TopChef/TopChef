from topchef.models.abstract_classes import JobListRequiringQuery
from topchef.database.models import Job as DatabaseJob


class JobList(JobListRequiringQuery):
    """
    Implements the interface to get all the jobs in the job list
    """
    @property
    def root_job_query(self):
        return self.session.query(DatabaseJob)

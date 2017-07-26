"""
Contains all things required for storing relational data. This is currently
done by a SQLite database.
"""
from .uuid_database_type import UUID
from .models import Job, Service, JobSet

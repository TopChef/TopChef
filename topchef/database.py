from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URI

ENGINE = create_engine(DATABASE_URI)

METADATA = MetaData(bind=ENGINE)

SESSION_FACTORY = sessionmaker(bind=ENGINE)

users_table = Table(
    'users', METADATA,
    Column('username', String(30), primary_key=True, nullable=False),
    Column('email', String(128), nullable=False)
)

jobs_table = Table(
    'jobs', METADATA,
    Column('job_id', Integer, primary_key=True, nullable=False),
    Column('username', Integer, ForeignKey('users.username'), nullable=False),
    Column('date_created', DateTime, nullable=False, default=datetime.now()),
    Column('status', Enum('QUEUED', 'IN_PROGRESS', 'DONE')),
    Column('date_started', DateTime, nullable=True),
    Column('date_completed', DateTime, nullable=True),
    Column('priority', Integer, nullable=False, default=10)
)

from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from .config import DATABASE_URI

ENGINE = create_engine(DATABASE_URI)

METADATA = MetaData(bind=ENGINE)

SESSION_FACTORY = sessionmaker(bind=ENGINE)

users_table = Table(
    'users', METADATA,
    Column('username', String(30), primary_key=True, nullable=False),
    Column('email', String(128), nullable=False)
)

job_table = Table(
    'jobs', METADATA,
    Column('job_id', Integer, primary_key=True, nullable=False),
    Column('owner', String(30), ForeignKey('users.username'), nullable=False),
    Column('due_date', DateTime, nullable=False, default=datetime.utcnow())
)


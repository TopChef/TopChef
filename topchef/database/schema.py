"""
Describes the database schema
"""
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy import MetaData, Table, Column, Integer, Boolean
from sqlalchemy import Enum
from datetime import datetime
from . import UUID

METADATA = MetaData()


services = Table(
    'services', METADATA,
    Column('service_id', UUID, primary_key=True, nullable=False),
    Column('name', String(30), nullable=False),
    Column('description', String(1000), nullable=False,
           default='No description'
           ),
    Column('last_checked_in', DateTime, nullable=False,
           default=datetime.utcnow()),
    Column('heartbeat_timeout_seconds', Integer, nullable=False, default=30),
    Column('is_service_available', Boolean, nullable=False)
)

jobs = Table(
    'jobs', METADATA,
    Column('job_id', UUID, primary_key=True, nullable=False),
    Column('service_id', UUID, ForeignKey('services.service_id'),
           nullable=False
           ),
    Column('date_submitted', DateTime, nullable=False,
           default=datetime.utcnow()),
    Column('status', Enum("REGISTERED", "WORKING", "COMPLETED"), 
           default="REGISTERED")
)

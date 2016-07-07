from sqlalchemy import create_engine
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy import MetaData, Table, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgres import UUID
import uuid

from .config import config

ENGINE = create_engine(config.DATABASE_URI)

METADATA = MetaData(bind=ENGINE)

SESSION_FACTORY = sessionmaker(bind=ENGINE)


class GUID(TypeDecorator):
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID)
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

services = Table(
    'services', METADATA,
    Column('service_id', GUID, primary_key=True, nullable=False),
    Column('name', String(30), nullable=False)
)

jobs = Table(
    'jobs', METADATA,
    Column('job_id', GUID, primary_key=True, nullable=False),
    Column('service_id', GUID, ForeignKey('services.service_id'),
           nullable=False
           ),
    Column('date_submitted', DateTime, nullable=False)
)
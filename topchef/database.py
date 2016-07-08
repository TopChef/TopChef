from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy import MetaData, Table, Column
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgres import UUID
import uuid

METADATA = MetaData()


class GUID(TypeDecorator):
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)

    def copy(self, *args, **kwargs):
        return GUID(*args, **kwargs)

services = Table(
    'services', METADATA,
    Column('service_id', GUID, primary_key=True, nullable=False),
    Column('name', String(30), nullable=False),
    Column('description', String(1000), nullable=False,
           default='No description'
           )
)

jobs = Table(
    'jobs', METADATA,
    Column('job_id', GUID, primary_key=True, nullable=False),
    Column('service_id', GUID, ForeignKey('services.service_id'),
           nullable=False
           ),
    Column('date_submitted', DateTime, nullable=False)
)
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column, String
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URI

ENGINE = create_engine(DATABASE_URI)

METADATA = MetaData()

SESSION_FACTORY = sessionmaker(bind=ENGINE)

users_table = Table(
    'users', METADATA,
    Column('username', String(30), primary_key=True, nullable=False),
    Column('email', String(128), nullable=False)
)


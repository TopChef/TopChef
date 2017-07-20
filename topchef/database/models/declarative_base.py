from ..schemas import database
from sqlalchemy.ext.declarative import declarative_base

BASE = declarative_base(metadata=database.metadata)

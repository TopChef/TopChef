"""
Defines a base class for creating mapped objects from SQLAlchemy. Any class
that has persistent attributes should subclass this class.
"""
from ..schemas import database
from sqlalchemy.ext.declarative import declarative_base

__all__ = ["BASE"]

BASE = declarative_base(metadata=database.metadata)

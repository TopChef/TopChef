"""
Contains different database schemas used to represent data
"""
from .abstract_database_schemas import AbstractDatabaseSchema
from .abstract_database_schemas import AbstractDatabaseSchemaWithJSONTable
from .database_schema import DatabaseSchema
from .database_schema_with_json_table import DatabaseSchemaWithJSONTable

database = DatabaseSchemaWithJSONTable()

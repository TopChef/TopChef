from topchef.database.schemas.database_schema_with_json_table import database
from topchef.database.models.declarative_base import BASE
from typing import Dict, Optional, Any


class JSONDocument(BASE):
    __table__ = database.json_objects

    id = __table__.c.document_id
    document = __table__.c.json

    def __init__(self, document: Dict[str, Optional[Any]]) -> None:
        self.document = document

from typing import List
from app import models
from sqlalchemy.orm import Session


class ChatflowUIServices:
    def create_bulk_chatflow(
        self,
        db: Session,
        *,
        nodes: List[models.NodeUI],
        edges: List[models.Edge]
    ):
        for node in nodes:
            db.add(node)
        for edge in edges:
            db.add(edge)
        db.commit()

        return


chatflow_ui = ChatflowUIServices()

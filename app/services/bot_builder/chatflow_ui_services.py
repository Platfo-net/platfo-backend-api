from typing import List
from app import models
from sqlalchemy.orm import Session


class ChatflowUIServices:
    def create_bulk_chatflow(
        self,
        db: Session,
        *,
        nodes: List[models.bot_builder.NodeUI],
        edges: List[models.bot_builder.Edge]
    ):
        for node in nodes:
            db.add(node)
        for edge in edges:
            db.add(edge)
        db.commit()

        return


chatflow_ui = ChatflowUIServices()

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

    def get_node_ui(self, db: Session, *, chatflow_id: int):
        return db.query(models.bot_builder.NodeUI).filter(
            models.bot_builder.NodeUI.chatflow_id == chatflow_id).all()

    def get_edge_ui(self, db: Session, *, chatflow_id: int):
        return db.query(models.bot_builder.Edge).filter(
            models.bot_builder.Edge.chatflow_id == chatflow_id).all()


chatflow_ui = ChatflowUIServices()

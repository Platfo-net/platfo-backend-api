from typing import List
from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder


class NodeServices(
        BaseServices[
            models.Node,
            schemas.NodeCreate,
            schemas.NodeUpdate
        ]):

    def get_nodes(
        self,
        db: Session,
        *,
        chatflow_id: UUID4
    ) -> List[schemas.Node]:
        return db.query(self.model).filter(
            self.model.chatflow_id == chatflow_id
        ).all()

    def create(
        self,
        db: Session,
        *,
        obj_in: schemas.NodeCreate
    ) -> schemas.Node:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, from_widget={})
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_widget(self, db: Session, *, obj_in: dict, node_id: UUID4):
        node = db.query(models.Node).filter(models.Node.id == node_id).first()
        node.widget = obj_in
        db.add(node)
        db.commit()
        db.refresh(node)
        return(node)

    def connect(self, db: Session, *, from_id: UUID4, node_id: UUID4):
        node = db.query(models.Node).filter(models.Node.id == node_id).first()
        from_widget = node.from_widget if node.from_widget else []
        from_widget.append(str(from_id))
        node.from_widget = None
        node.from_widget = set(from_widget)

        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    def add_quick_reply(
        self,
        db: Session,
        *,
        obj_in: List[dict],
        node_id: UUID4
    ):
        node = db.query(models.Node).filter(models.Node.id == node_id).first()
        node.quick_replies = obj_in
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    def get_next_node(self, db: Session, *, from_id: UUID4):
        return db.query(models.Node).filter(
            models.Node.from_widget.contains([str(from_id)])
        ).first()

    def get_chatflow_head_node(self, db: Session, *, chatflow_id):
        return db.query(models.Node).filter(
            models.Node.chatflow_id == chatflow_id,
            models.Node.is_head == True  # noqa
        ).first()

    def create_bulk_nodes(self, db: Session, *, nodes: List[models.Node]):
        for node in nodes:
            db.add(node)
        db.commit()
        return

    def delete_chatflow_nodes(self, db: Session, *, chatflow_id: UUID4):
        return db.query(self.model).filter(
            self.model.chatflow_id == chatflow_id
        ).delete()


node = NodeServices(models.Node)

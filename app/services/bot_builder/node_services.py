from typing import List, Optional
from pydantic import UUID4
from app.services.base import BaseServices
from app import models, schemas
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

ModelType = models.bot_builder.Node
CreateSchemaType = schemas.bot_builder.NodeCreate
UpdateSchemaType = schemas.bot_builder.NodeUpdate

class NodeServices(
    BaseServices[
        ModelType,
        CreateSchemaType,
        UpdateSchemaType,
    ]
):
    def get_nodes(
        self, db: Session, *, chatflow_id: UUID4
    ) -> List[schemas.bot_builder.Node]:
        return db.query(self.model).filter(self.model.chatflow_id == chatflow_id).all()

    def create(
        self, db: Session, *, obj_in: CreateSchemaType
    ) -> schemas.bot_builder.Node:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, from_widget={})
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def add_widget(self, db: Session, *, obj_in: dict, node_id: UUID4):
        node = (
            db.query(models.bot_builder.Node)
            .filter(models.bot_builder.Node.id == node_id)
            .first()
        )
        node.widget = obj_in
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    def connect(self, db: Session, *, from_id: UUID4, node_id: UUID4):
        node = (
            db.query(models.bot_builder.Node)
            .filter(models.bot_builder.Node.id == node_id)
            .first()
        )
        from_widget = node.from_widget if node.from_widget else []
        from_widget.append(str(from_id))
        node.from_widget = None
        node.from_widget = set(from_widget)
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    def add_quick_reply(self, db: Session, *, obj_in: List[dict], node_id: UUID4):
        node = (
            db.query(models.bot_builder.Node)
            .filter(models.bot_builder.Node.id == node_id)
            .first()
        )
        node.quick_replies = obj_in
        db.add(node)
        db.commit()
        db.refresh(node)
        return node

    def get_next_node(
        self, db: Session, *, from_id: UUID4
    ) -> Optional[models.bot_builder.Node]:
        return (
            db.query(models.bot_builder.Node)
            .filter(models.bot_builder.Node.from_widget.contains([str(from_id)]))
            .first()
        )

    def get_chatflow_head_node(self, db: Session, *, chatflow_id):
        return (
            db.query(models.bot_builder.Node)
            .filter(
                models.bot_builder.Node.chatflow_id == chatflow_id,
                models.bot_builder.Node.is_head == True,  # noqa
            )
            .first()
        )

    def create_bulk_nodes(self, db: Session, *, nodes: List[models.bot_builder.Node]):
        for node in nodes:
            db.add(node)
        db.commit()
        return

    def delete_chatflow_nodes(self, db: Session, *, chatflow_id: UUID4):
        return (
            db.query(self.model).filter(self.model.chatflow_id == chatflow_id).delete()
        )

    def get_widget_chatflow_id(self, db: Session , * , widget_id: UUID4)-> UUID4:
        node =  db.query(self.model).filter(self.model.id == id).first()
        return node.chatflow_id


node = NodeServices(models.bot_builder.Node)



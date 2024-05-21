from abc import ABC, abstractmethod

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session


class BaseRepository(ABC):
    """
    Base class for repositories
    """

    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self):
        return self._session

    @abstractmethod
    def get_by_id(self, pk):
        ...

    @abstractmethod
    def get_by_uuid(self, pk):
        ...

    @abstractmethod
    def get_multi(self, skip=0, limit=100):
        ...

    @abstractmethod
    def get_multi_by_user_id(self, user_id, skip=0, limit=100):
        ...

    @abstractmethod
    def create(self, obj_in):
        ...

    @abstractmethod
    def create_atomic(self, obj_in):
        ...

    @abstractmethod
    def update(self, db_obj, obj_in):
        ...

    @abstractmethod
    def delete(self, pk):
        ...


class CRUDBRepository(BaseRepository):
    model = None

    def get_by_id(self, pk):
        return self.session.query(self.model).filter(self.model.id == pk).first()

    def get_by_uuid(self, uuid):
        return self.session.query(self.model).filter(self.model.uuid == uuid).first()

    def get_multi(self, skip=0, limit=100):
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def get_multi_by_user_id(self, user_id, skip=0, limit=100):
        return self.session.query(self.model). \
            filter(self.model.user_id == user_id).offset(skip).limit(limit).all()

    def create(self, obj_in):
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def create_atomic(self, obj_in):
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        return db_obj

    def update(self, db_obj, obj_in):
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, pk):
        obj = self.session.query(self.model).get(pk)
        self.session.delete(obj)
        self.session.commit()
        return obj

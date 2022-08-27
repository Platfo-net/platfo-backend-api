

# from typing import Optional

from typing import List
from app.services.base import BaseServices
from sqlalchemy.orm import Session
from app import models, schemas
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4


class CategoryServices(
    BaseServices
    [
        models.Category,
        schemas.CategoryCreate,
        schemas.CategoryUpdate
    ]
):
    def get_multi(db:Session , * , page: int = 1 , page_size: int =20):
        
        items = db.query(models.Category)
        
        return 



category = CategoryServices(models.Category)

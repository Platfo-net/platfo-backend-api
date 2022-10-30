from typing import Any

from starlette import status

from app import models, services, schemas
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from pydantic.types import UUID4
from app.constants.errors import Error

from app.constants.role import Role


router = APIRouter(prefix="/postman", tags=["Postman"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def test():
    from app.core.postman import tasks
    tasks.campaign_terminal.delay()
    return 'successssssssssssssss'



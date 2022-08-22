import requests
from typing import List
from fastapi import APIRouter, HTTPException
from app import schemas, services
from app.core.config import settings
from app.core.cache import commence_redis

router = APIRouter(prefix="/message", tags=["Messages"])


@router.get("/archive/{page_id}/{contact_igs_id}",
            response_model=List[schemas.Message])
def get_archive(
    *,
    contact_igs_id: str,
    page_id: str,
    skip: int = 0,
    limit: int = 20,
):

    return services.message.get_pages_messages(
        contact_igs_id=contact_igs_id,
        page_id=page_id,
        skip=skip,
        limit=limit
    )

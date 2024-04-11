

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.message_builder import MessageBuilderMessage
from app.api import deps
from fastapi.responses import RedirectResponse


router = APIRouter(
    prefix='/message-builder', tags=['MessageBuilder'], include_in_schema=False
)


@router.get('/redirect')
def redirect_url(
    *,
    db: Session = Depends(deps.get_db),
    tgWebAppStartParam: str,
) -> Any:
    message = db.query(MessageBuilderMessage).filter(
        MessageBuilderMessage.short_url == tgWebAppStartParam
    ).first()

    if not message:
        return {"message": "Invalid url"}

    return RedirectResponse(url=message.short_url)

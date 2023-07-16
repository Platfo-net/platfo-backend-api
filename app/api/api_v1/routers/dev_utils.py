from typing import Any

from fastapi import APIRouter, Depends, Security
from redis import Redis

from app import models
from app.api import deps
from app.constants.role import Role

router = APIRouter(prefix='/dev', tags=['Dev Tools'])


@router.get('/sms-code-delete')
def delete_(
    *,
    redis_client: Redis = Depends(deps.get_redis_client_for_user_activation),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[
            Role.ADMIN['name'],
            Role.DEVELOPER['name'],
        ],
    ),
) -> Any:

    keys = redis_client.keys()
    for key in keys:
        redis_client.delete(key)

    return

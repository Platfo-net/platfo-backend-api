import requests
from typing import List
from fastapi import APIRouter, HTTPException
from app import schemas, services
from app.core.config import settings
from app.core.cache import commence_redis

router = APIRouter(prefix="/message", tags=["Messages"])


# @router.post("/", response_model=schemas.Message)
def create_message(
    *,
    obj_in: schemas.MessageCreate,
):
    if obj_in.direction == "In":
        contact = services.contact.get_by_page_id(
            page_id=obj_in.from_page_id
        )
        if not contact:
            contact_in = schemas.ContactCreate(
                contact_igs_id=obj_in.from_page_id,
                user_page_id=obj_in.to_page_id,
                user_id=obj_in.user_id)
            services.contact.create(obj_in=contact_in)

            try:
                facebook_page_token = commence_redis(
                    page_id=obj_in.to_page_id
                )['facebook_page_token']
            except Exception:
                raise HTTPException(status_code=400)

            url = "{}/{}/{}".format(
                settings.FACEBOOK_GRAPH_BASE_URL,
                settings.FACEBOOK_GRAPH_VERSION,
                obj_in.from_page_id)
            params = dict(
                fields="name,username,profile_pic,follower_count,"
                       "is_user_follow_business,is_business_follow_user",
                access_token=facebook_page_token
            )
            res = requests.get(url=url, params=params)
            if res.status_code == 200:
                username = res.json()['username']
                profile_image = res.json()['profile_pic']
                information = dict(username=username,
                                   profile_image=profile_image)
                services.contact.set_information(
                    information=information,
                    contact_igs_id=obj_in.from_page_id
                )
            else:
                pass

    if obj_in.direction == "IN":
        services.contact.update_last_message_at(
            contact_igs_id=obj_in.from_page_id)

    else:
        services.contact.update_last_message_at(
            contact_igs_id=obj_in.to_page_id)

    return services.message.create(obj_in=obj_in)


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

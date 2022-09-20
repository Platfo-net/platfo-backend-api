import logging
import requests

from typing import Any

from app import services, models, schemas
from app.api import deps
from app.constants.errors import Error
from app.constants.role import Role
from fastapi import APIRouter, Depends, \
    HTTPException, Security, status
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter(prefix="/instagram", tags=["Instagram"])


@router.post("")
def connect_instagram_page(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.ConnectPage,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
) -> Any:

    # get user long lived token

    params = dict(grant_type="fb_exchange_token",
                  client_id=settings.FACEBOOK_APP_ID,
                  client_secret=settings.FACEBOOK_APP_SECRET,
                  redirect_uri='https://botinow.com/api/auth/callback/facebook',  # noqa
                  fb_exchange_token=obj_in.facebook_user_token)

    get_long_lived_token_url = "{}/{}/oauth/access_token".format(
        settings.FACEBOOK_GRAPH_BASE_URL, settings.FACEBOOK_GRAPH_VERSION
    )

    res = requests.get(get_long_lived_token_url, params=params)
    long_lived_user_access_token = res.json()['access_token']

    facebook_account = services.facebook_account.get_by_facebook_user_id(
        db,
        facebook_user_id=obj_in.facebook_user_id
    )

    if facebook_account:
        facebook_account_in = schemas.FacebookAccountUpdate(
            facebook_user_long_lived_token=long_lived_user_access_token,
            facebook_user_id=obj_in.facebook_user_id,
            user_id=current_user.id
        )
        facebook_account = services.facebook_account.update(
            db, db_obj=facebook_account, obj_in=facebook_account_in)
    else:
        facebook_account_in = schemas.FacebookAccountCreate(
            facebook_user_long_lived_token=long_lived_user_access_token,
            facebook_user_id=obj_in.facebook_user_id,
            user_id=current_user.id
        )
        facebook_account = services.facebook_account.create(
            db, obj_in=facebook_account_in)

    # get pages long lived token

    params = dict(access_token=long_lived_user_access_token)

    page_long_lived_token_url = "{}/{}/{}/accounts".format(
        settings.FACEBOOK_GRAPH_BASE_URL,
        settings.FACEBOOK_GRAPH_VERSION,
        obj_in.facebook_user_id
    )
    res = requests.get(page_long_lived_token_url, params=params)

    pages = res.json()["data"]

    # get ig id
    for page in pages:
        try:
            params = dict(
                access_token=page["access_token"],
                fields='connected_instagram_account',
            )
            get_instagram_page_id_url = "{}/{}/{}/".format(
                settings.FACEBOOK_GRAPH_BASE_URL,
                settings.FACEBOOK_GRAPH_VERSION,
                page['id'],
            )
            res = requests.get(get_instagram_page_id_url, params=params)
            instagram_page_id = res.json()['connected_instagram_account']['id']
            subscribe_url = "{}/{}/{}/subscribed_apps".format(
                settings.FACEBOOK_GRAPH_BASE_URL,
                settings.FACEBOOK_GRAPH_VERSION,
                page['id']
            )
            params = dict(
                subscribed_fields="name",
                access_token=page["access_token"],
            )
            res = requests.post(subscribe_url, params=params)
            print(res.json())
            params = dict(
                fields="username,profile_picture_url,"
                       "followers_count,follows_count,biography,"
                       "website,ig_id,name",
                access_token=page["access_token"],
            )

            get_page_info_url = "{}/{}/{}".format(
                settings.FACEBOOK_GRAPH_BASE_URL,
                settings.FACEBOOK_GRAPH_VERSION,
                instagram_page_id
            )

            res = requests.get(get_page_info_url, params=params)

            page_details = res.json()

            instagram_page = services.instagram_page\
                .get_page_by_instagram_page_id(
                    db, instagram_page_id=instagram_page_id
                )
            if instagram_page:
                instagram_page_in = schemas.InstagramPageUpdate(
                    facebook_account_id=facebook_account.id,
                    facebook_page_id=page.get("id", None),
                    facebook_page_token=page.get("access_token", None),
                    instagram_page_id=instagram_page_id,
                    instagram_username=page_details.get("username", None),
                    instagram_profile_picture_url=page_details.get("profile_picture_url", None),  # noqa
                    information=dict(
                         website=page_details.get("website", None),
                         ig_id=page_details.get('ig_id', None),
                         followers_count=page_details.get(
                             'followers_count', None),
                         follows_count=page_details.get('follows_count', None),
                         biography=page_details.get('biography', None),
                         name=page_details.get("name", None)
                                     )
                )
                services.instagram_page.update(
                    db,
                    db_obj=instagram_page,
                    obj_in=instagram_page_in
                )
            else:
                instagram_page_in = schemas.InstagramPageCreate(
                    facebook_account_id=facebook_account.id,
                    facebook_page_id=page.get("id", None),
                    facebook_page_token=page.get("access_token", None),
                    instagram_page_id=instagram_page_id,
                    instagram_username=page_details.get("username", None),
                    instagram_profile_picture_url=page_details.get("profile_picture_url", None),  # noqa
                    information=dict(
                         website=page_details.get("website", None),
                         ig_id=page_details.get('ig_id', None),
                         followers_count=page_details.get(
                             'followers_count', None),
                         follows_count=page_details.get('follows_count', None),
                         biography=page_details.get('biography', None),
                         name=page_details.get("name", None)
                                     )
                    )

                services.instagram_page.create(db, obj_in=instagram_page_in)

        except Exception as e:
            pass

    return


@router.delete("", status_code=status.HTTP_200_OK)
def facebook_disconnect_page(
        *,
        db: Session = Depends(deps.get_db),
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    facebook_account = services.facebook_account\
        .get_by_user_id(db, user_id=current_user.id)
    if not facebook_account:
        raise HTTPException(
            detail=Error.ACCOUNT_NOT_FOUND["detail"],
            status_code=Error.ACCOUNT_NOT_FOUND["status_code"]
        )
    services.instagram_page.\
        delete_by_facebook_account_id(db, account_id=facebook_account.id)
    services.facebook_account.delete_by_user_id(db, user_id=current_user.id)

    return


@router.get('/get/{instagram_page_id}', response_model=schemas.InstagramPage)
def get_page_data_by_instagram_page_id(
        *,
        db: Session = Depends(deps.get_db),
        instagram_page_id: str
):
    obj_instagram = services.instagram_page.get_page_by_ig_id(
        db, ig_id=instagram_page_id)
    return obj_instagram


@router.get('/get_by_page_id/{page_id}', response_model=schemas.InstagramPage)
def get_page_data_by_page_id(
        *,
        db: Session = Depends(deps.get_db),
        page_id: str
):
    obj_instagram = services.instagram_page.get_by_page_id(db, page_id=page_id)

    return obj_instagram

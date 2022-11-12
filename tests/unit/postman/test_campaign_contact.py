from sqlalchemy.orm import Session
from app import services, schemas, models
from app.core.config import settings
from tests.unit.postman import helper


def test_add_contacts_to_campaign(db: Session):
    user = services.user.get_by_email(db, email=settings.FIRST_USER_EMAIL)
    account = helper.create_instagram_account(db, facebook_page_id="20")

    campaign = helper.create_campaign(db, user.id, account.facebook_page_id)

    contact_1 = services.live_chat.contact.create(
        db,
        obj_in=schemas.live_chat.ContactCreate(
            user_page_id=account.facebook_page_id,
            user_id=user.id,
            contact_igs_id="1"
        )
    )
    contact_2 = services.live_chat.contact.create(
        db,
        obj_in=schemas.live_chat.ContactCreate(
            user_page_id=account.facebook_page_id,
            user_id=user.id,
            contact_igs_id="2"
        )
    )
    contact_3 = services.live_chat.contact.create(
        db,
        obj_in=schemas.live_chat.ContactCreate(
            user_page_id=account.facebook_page_id,
            user_id=user.id,
            contact_igs_id="3"
        )
    )

    schemas.postman.CampaignContactCreate(
        contact_id=contact_1.id,
        contact_igs_id=contact_1.contact_igs_id
    )

    contacts_in = [
        schemas.postman.CampaignContactCreate(
            contact_id=contact_1.id,
            contact_igs_id=contact_1.contact_igs_id
        ),
        schemas.postman.CampaignContactCreate(
            contact_id=contact_2.id,
            contact_igs_id=contact_2.contact_igs_id
        ),
        schemas.postman.CampaignContactCreate(
            contact_id=contact_3.id,
            contact_igs_id=contact_3.contact_igs_id
        )
    ]

    campaign_contacts = services.postman.campaign_contact.create_bulk(
        db, campaign_id=campaign.id, contacts=contacts_in)

    contacts_id = [
        contact_1.id, contact_2.id, contact_3.id
    ]
    contacts = services.live_chat.contact.get_bulk(db, contacts_id=contacts_id)

    assert len(contacts) == 3
    assert type(contacts) == list

    db_contacts_id = [c.id for c in contacts]

    assert contact_1.id in db_contacts_id
    assert contact_2.id in db_contacts_id
    assert contact_3.id in db_contacts_id

    assert type(campaign_contacts) == list
    for campaign_contact in campaign_contacts:
        assert isinstance(campaign_contact, models.postman.CampaignContact)

    db_campaing_contatcs_igs_id = [c.contact_igs_id for c in campaign_contacts]

    assert contact_1.contact_igs_id in db_campaing_contatcs_igs_id
    assert contact_2.contact_igs_id in db_campaing_contatcs_igs_id
    assert contact_3.contact_igs_id in db_campaing_contatcs_igs_id

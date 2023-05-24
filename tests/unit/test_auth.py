from sqlalchemy.orm import Session

from app import models
from app.core.security import create_token

from .fixtures import sample_user  # noqa


def test_create_access_token(db: Session, sample_user: models.User): # noqa
    token = create_token(db, user=sample_user)
    assert token.access_token is not None

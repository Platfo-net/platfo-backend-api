from sqlalchemy.orm import Session

from app import services
from app.core.config import settings


def create_user(db: Session):
    return services.user.get_by_email(db=db, email=settings.FIRST_USER_EMAIL)

from app import services
from app.schemas.user import UserCreate
from sqlalchemy.orm import Session
from tests.utils.utils import random_lower_string


def create_sample_user(db: Session):
    email = "user@example.com",
    is_active = True,
    full_name = random_lower_string(),
    phone_number = "09123456789",
    password = "Abcd@1234"
    user_in = UserCreate(
        email=email,
        is_active=is_active,
        full_name=full_name,
        phone_number=phone_number,
        password=password
    )
    return services.user.create(db, obj_in=user_in)

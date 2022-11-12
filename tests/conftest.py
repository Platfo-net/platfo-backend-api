from typing import Generator
import pytest
from app.api.deps import get_db
from app.db.session import TestingSessionLocal
from app.main import app
from fastapi.testclient import TestClient


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db() -> Generator:
    yield TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c

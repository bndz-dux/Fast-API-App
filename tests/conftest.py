import os

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-with-enough-length-for-hs256")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402
from app.services import user_service  # noqa: E402

API = "/api/v1"


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with session_factory() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin(db_session: Session) -> User:
    return user_service.create_user(
        db_session,
        UserCreate(
            email="admin@example.com",
            username="admin",
            first_name="Ad",
            last_name="Min",
            password="adminpass",
            is_admin=True,
        ),
    )


def login(client: TestClient, username: str, password: str) -> dict[str, str]:
    r = client.post(f"{API}/auth/login", data={"username": username, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def register(client: TestClient, username: str, password: str = "password123") -> dict[str, str]:
    r = client.post(
        f"{API}/auth/register",
        json={
            "email": f"{username}@example.com",
            "username": username,
            "first_name": "First",
            "last_name": "Last",
            "password": password,
        },
    )
    assert r.status_code == 201, r.text
    return login(client, username, password)

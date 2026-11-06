"""Create the first admin user from FIRST_ADMIN_* settings: python -m app.initial_data"""

from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.user import UserCreate
from app.services import user_service


def main() -> None:
    if not (settings.FIRST_ADMIN_EMAIL and settings.FIRST_ADMIN_USERNAME and settings.FIRST_ADMIN_PASSWORD):
        raise SystemExit("FIRST_ADMIN_EMAIL, FIRST_ADMIN_USERNAME and FIRST_ADMIN_PASSWORD must be set")

    with SessionLocal() as db:
        if user_service.get_by_login(db, settings.FIRST_ADMIN_USERNAME):
            print("Admin user already exists")
            return
        user_service.create_user(
            db,
            UserCreate(
                email=settings.FIRST_ADMIN_EMAIL,
                username=settings.FIRST_ADMIN_USERNAME,
                first_name="System",
                last_name="Admin",
                password=settings.FIRST_ADMIN_PASSWORD,
                is_admin=True,
            ),
        )
        print(f"Admin user '{settings.FIRST_ADMIN_USERNAME}' created")


if __name__ == "__main__":
    main()

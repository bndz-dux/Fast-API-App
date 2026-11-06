from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ConflictError, NotFoundError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserRegister, UserUpdate, UserUpdateMe
from app.services import company_service
from app.services.base import apply_changes, paginate


def get_user(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    return user


def get_by_login(db: Session, login: str) -> User | None:
    stmt = select(User).where(or_(User.email == login.lower(), User.username == login))
    return db.scalar(stmt)


def _ensure_unique(
    db: Session, *, email: str | None = None, username: str | None = None, exclude_id: int | None = None
) -> None:
    for column, value in ((User.email, email), (User.username, username)):
        if value is None:
            continue
        stmt = select(User.id).where(column == value)
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        if db.scalar(stmt) is not None:
            raise ConflictError(f"{column.key.capitalize()} '{value}' is already taken")


def list_users(
    db: Session,
    *,
    skip: int,
    limit: int,
    company_id: int | None = None,
    is_active: bool | None = None,
    search: str | None = None,
) -> tuple[list[User], int]:
    stmt = select(User).order_by(User.id)
    if company_id is not None:
        stmt = stmt.where(User.company_id == company_id)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(pattern),
                User.email.ilike(pattern),
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
            )
        )
    return paginate(db, stmt, skip, limit)


def create_user(db: Session, data: UserRegister | UserCreate) -> User:
    fields = data.model_dump(exclude={"password"})
    fields["email"] = fields["email"].lower()
    _ensure_unique(db, email=fields["email"], username=fields["username"])
    if fields.get("company_id") is not None:
        company_service.get_company(db, fields["company_id"])

    user = User(**fields, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, data: UserUpdateMe | UserUpdate) -> User:
    changes = data.model_dump(exclude_unset=True)
    if "email" in changes:
        changes["email"] = changes["email"].lower()
    _ensure_unique(db, email=changes.get("email"), username=changes.get("username"), exclude_id=user.id)
    if changes.get("company_id") is not None:
        company_service.get_company(db, changes["company_id"])
    if "password" in changes:
        user.hashed_password = hash_password(changes.pop("password"))

    apply_changes(user, changes)
    db.commit()
    db.refresh(user)
    return user


def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, user.hashed_password):
        raise BadRequestError("Current password is incorrect")
    user.hashed_password = hash_password(new_password)
    db.commit()


def delete_user(db: Session, user: User) -> None:
    db.delete(user)
    db.commit()


def authenticate(db: Session, login: str, password: str) -> User | None:
    user = get_by_login(db, login)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user

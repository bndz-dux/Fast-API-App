from fastapi import APIRouter, Depends, status

from app.api.deps import AdminUser, CurrentUser, PaginationDep, SearchQuery, SessionDep, get_current_admin
from app.core.exceptions import BadRequestError
from app.schemas.common import Page
from app.schemas.user import PasswordChange, UserCreate, UserRead, UserUpdate, UserUpdateMe
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(data: UserUpdateMe, db: SessionDep, current_user: CurrentUser):
    return user_service.update_user(db, current_user, data)


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(data: PasswordChange, db: SessionDep, current_user: CurrentUser) -> None:
    user_service.change_password(db, current_user, data.current_password, data.new_password)


@router.get("", response_model=Page[UserRead], dependencies=[Depends(get_current_admin)])
def list_users(
    db: SessionDep,
    page: PaginationDep,
    company_id: int | None = None,
    is_active: bool | None = None,
    search: SearchQuery = None,
):
    items, total = user_service.list_users(
        db, skip=page.skip, limit=page.limit, company_id=company_id, is_active=is_active, search=search
    )
    return {"items": items, "total": total, "skip": page.skip, "limit": page.limit}


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
def create_user(data: UserCreate, db: SessionDep):
    return user_service.create_user(db, data)


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_admin)])
def read_user(user_id: int, db: SessionDep):
    return user_service.get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserRead, dependencies=[Depends(get_current_admin)])
def update_user(user_id: int, data: UserUpdate, db: SessionDep):
    user = user_service.get_user(db, user_id)
    return user_service.update_user(db, user, data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: SessionDep, admin: AdminUser) -> None:
    if user_id == admin.id:
        raise BadRequestError("Admins cannot delete themselves")
    user_service.delete_user(db, user_service.get_user(db, user_id))

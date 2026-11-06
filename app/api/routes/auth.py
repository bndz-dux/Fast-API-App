from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.schemas.user import UserRead, UserRegister
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(db: SessionDep, form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Log in with username or email and receive a JWT bearer token."""
    user = user_service.authenticate(db, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return Token(access_token=create_access_token(user.id))


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: SessionDep):
    """Self sign-up. Always creates a regular (non-admin) user without a company."""
    return user_service.create_user(db, data)

from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, EmailStr, StringConstraints

from app.schemas.common import PatchSchema

Username = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$"),
]
PersonName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
# bcrypt only uses the first 72 bytes
Password = Annotated[str, StringConstraints(min_length=8, max_length=72)]


class UserBase(BaseModel):
    email: EmailStr
    username: Username
    first_name: PersonName
    last_name: PersonName


class UserRegister(UserBase):
    password: Password


class UserCreate(UserRegister):
    company_id: int | None = None
    is_active: bool = True
    is_admin: bool = False


class UserUpdateMe(PatchSchema):
    email: EmailStr | None = None
    username: Username | None = None
    first_name: PersonName | None = None
    last_name: PersonName | None = None


class UserUpdate(UserUpdateMe):
    nullable_fields: ClassVar[frozenset[str]] = frozenset({"company_id"})

    password: Password | None = None
    company_id: int | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: Password


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_admin: bool
    company_id: int | None
    created_at: datetime

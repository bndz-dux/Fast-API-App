from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.company import CompanyMode
from app.schemas.common import PatchSchema

CompanyName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
Rating = Annotated[float, Field(ge=0, le=5)]


class CompanyBase(BaseModel):
    name: CompanyName
    description: str | None = None
    mode: CompanyMode = CompanyMode.ACTIVE
    rating: Rating = 0


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(PatchSchema):
    nullable_fields: ClassVar[frozenset[str]] = frozenset({"description"})

    name: CompanyName | None = None
    description: str | None = None
    mode: CompanyMode | None = None
    rating: Rating | None = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

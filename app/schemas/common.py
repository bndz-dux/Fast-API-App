from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel, model_validator

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class PatchSchema(BaseModel):
    """Partial update: omitted fields stay untouched, explicit null only for nullable columns."""

    nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def _reject_null_for_required_fields(self):
        for name in self.model_fields_set:
            if getattr(self, name) is None and name not in self.nullable_fields:
                raise ValueError(f"'{name}' cannot be null")
        return self

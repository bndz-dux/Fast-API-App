from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

T = TypeVar("T")


def paginate(db: Session, stmt: Select[tuple[T]], skip: int, limit: int) -> tuple[list[T], int]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    items = list(db.scalars(stmt.offset(skip).limit(limit)))
    return items, total


def apply_changes(obj: Any, changes: dict[str, Any]) -> None:
    for field, value in changes.items():
        setattr(obj, field, value)

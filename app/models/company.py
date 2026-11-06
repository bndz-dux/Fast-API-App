import enum
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class CompanyMode(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Company(TimestampMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (CheckConstraint("rating >= 0 AND rating <= 5", name="rating_range"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    mode: Mapped[CompanyMode] = mapped_column(
        Enum(CompanyMode, name="company_mode"),
        default=CompanyMode.ACTIVE,
        server_default=CompanyMode.ACTIVE.value,
    )
    rating: Mapped[float] = mapped_column(Float, default=0, server_default="0")

    users: Mapped[list["User"]] = relationship(back_populates="company")

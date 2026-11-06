from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.company import Company, CompanyMode
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.services.base import apply_changes, paginate


def get_company(db: Session, company_id: int) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise NotFoundError(f"Company {company_id} not found")
    return company


def _ensure_name_available(db: Session, name: str, exclude_id: int | None = None) -> None:
    stmt = select(Company.id).where(func.lower(Company.name) == name.lower())
    if exclude_id is not None:
        stmt = stmt.where(Company.id != exclude_id)
    if db.scalar(stmt) is not None:
        raise ConflictError(f"Company '{name}' already exists")


def list_companies(
    db: Session,
    *,
    skip: int,
    limit: int,
    mode: CompanyMode | None = None,
    search: str | None = None,
) -> tuple[list[Company], int]:
    stmt = select(Company).order_by(Company.id)
    if mode is not None:
        stmt = stmt.where(Company.mode == mode)
    if search:
        stmt = stmt.where(Company.name.ilike(f"%{search}%"))
    return paginate(db, stmt, skip, limit)


def create_company(db: Session, data: CompanyCreate) -> Company:
    _ensure_name_available(db, data.name)
    company = Company(**data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def update_company(db: Session, company: Company, data: CompanyUpdate) -> Company:
    changes = data.model_dump(exclude_unset=True)
    if "name" in changes:
        _ensure_name_available(db, changes["name"], exclude_id=company.id)
    apply_changes(company, changes)
    db.commit()
    db.refresh(company)
    return company


def delete_company(db: Session, company: Company) -> None:
    db.delete(company)
    db.commit()

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, PaginationDep, SearchQuery, SessionDep, get_current_admin
from app.models.company import CompanyMode
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.schemas.common import Page
from app.services import company_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=Page[CompanyRead])
def list_companies(
    db: SessionDep,
    _: CurrentUser,
    page: PaginationDep,
    mode: CompanyMode | None = None,
    search: SearchQuery = None,
):
    items, total = company_service.list_companies(
        db, skip=page.skip, limit=page.limit, mode=mode, search=search
    )
    return {"items": items, "total": total, "skip": page.skip, "limit": page.limit}


@router.get("/{company_id}", response_model=CompanyRead)
def read_company(company_id: int, db: SessionDep, _: CurrentUser):
    return company_service.get_company(db, company_id)


@router.post(
    "",
    response_model=CompanyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
def create_company(data: CompanyCreate, db: SessionDep):
    return company_service.create_company(db, data)


@router.patch("/{company_id}", response_model=CompanyRead, dependencies=[Depends(get_current_admin)])
def update_company(company_id: int, data: CompanyUpdate, db: SessionDep):
    company = company_service.get_company(db, company_id)
    return company_service.update_company(db, company, data)


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
def delete_company(company_id: int, db: SessionDep) -> None:
    company_service.delete_company(db, company_service.get_company(db, company_id))

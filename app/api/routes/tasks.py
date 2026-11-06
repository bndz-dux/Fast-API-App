from fastapi import APIRouter, status

from app.api.deps import CurrentUser, PaginationDep, SearchQuery, SessionDep
from app.models.task import TaskPriority, TaskStatus
from app.schemas.common import Page
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=Page[TaskRead])
def list_tasks(
    db: SessionDep,
    current_user: CurrentUser,
    page: PaginationDep,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    owner_id: int | None = None,
    search: SearchQuery = None,
):
    """Regular users see only their own tasks; admins see all and may filter by `owner_id`."""
    items, total = task_service.list_tasks(
        db,
        current_user=current_user,
        skip=page.skip,
        limit=page.limit,
        owner_id=owner_id,
        status=status,
        priority=priority,
        search=search,
    )
    return {"items": items, "total": total, "skip": page.skip, "limit": page.limit}


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: SessionDep, current_user: CurrentUser):
    return task_service.create_task(db, data, current_user)


@router.get("/{task_id}", response_model=TaskRead)
def read_task(task_id: int, db: SessionDep, current_user: CurrentUser):
    return task_service.get_task(db, task_id, current_user)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, data: TaskUpdate, db: SessionDep, current_user: CurrentUser):
    task = task_service.get_task(db, task_id, current_user)
    return task_service.update_task(db, task, data, current_user)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: SessionDep, current_user: CurrentUser) -> None:
    task_service.delete_task(db, task_service.get_task(db, task_id, current_user))

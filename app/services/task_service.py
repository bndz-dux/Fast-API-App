from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import user_service
from app.services.base import apply_changes, paginate


def get_task(db: Session, task_id: int, current_user: User) -> Task:
    task = db.get(Task, task_id)
    # 404 instead of 403 so other users' task ids are not disclosed
    if task is None or (not current_user.is_admin and task.owner_id != current_user.id):
        raise NotFoundError(f"Task {task_id} not found")
    return task


def _resolve_owner_id(db: Session, owner_id: int | None, current_user: User) -> int:
    if owner_id is None or owner_id == current_user.id:
        return current_user.id
    if not current_user.is_admin:
        raise PermissionDeniedError("Only admins can assign tasks to other users")
    return user_service.get_user(db, owner_id).id


def list_tasks(
    db: Session,
    *,
    current_user: User,
    skip: int,
    limit: int,
    owner_id: int | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    search: str | None = None,
) -> tuple[list[Task], int]:
    stmt = select(Task).order_by(Task.id.desc())
    if not current_user.is_admin:
        stmt = stmt.where(Task.owner_id == current_user.id)
    elif owner_id is not None:
        stmt = stmt.where(Task.owner_id == owner_id)
    if status is not None:
        stmt = stmt.where(Task.status == status)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(or_(Task.summary.ilike(pattern), Task.description.ilike(pattern)))
    return paginate(db, stmt, skip, limit)


def create_task(db: Session, data: TaskCreate, current_user: User) -> Task:
    task = Task(
        **data.model_dump(exclude={"owner_id"}),
        owner_id=_resolve_owner_id(db, data.owner_id, current_user),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task: Task, data: TaskUpdate, current_user: User) -> Task:
    changes = data.model_dump(exclude_unset=True)
    if "owner_id" in changes:
        changes["owner_id"] = _resolve_owner_id(db, changes["owner_id"], current_user)
    apply_changes(task, changes)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()

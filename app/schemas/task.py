from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.models.task import TaskPriority, TaskStatus
from app.schemas.common import PatchSchema

Summary = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]


class TaskBase(BaseModel):
    summary: Summary
    description: str | None = None
    status: TaskStatus = TaskStatus.NEW
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskCreate(TaskBase):
    owner_id: int | None = Field(
        default=None, description="Assign to another user (admin only). Defaults to the current user."
    )


class TaskUpdate(PatchSchema):
    nullable_fields: ClassVar[frozenset[str]] = frozenset({"description"})

    summary: Summary | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    owner_id: int | None = Field(default=None, description="Reassign task (admin only).")


class TaskRead(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

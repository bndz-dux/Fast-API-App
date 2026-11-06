"""initial schema: companies, users, tasks

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-06

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

company_mode = sa.Enum("ACTIVE", "INACTIVE", name="company_mode")
task_status = sa.Enum("NEW", "IN_PROGRESS", "DONE", name="task_status")
task_priority = sa.Enum("LOW", "MEDIUM", "HIGH", "URGENT", name="task_priority")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("mode", company_mode, server_default="ACTIVE", nullable=False),
        sa.Column("rating", sa.Float(), server_default="0", nullable=False),
        *_timestamps(),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="ck_companies_rating_range"),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
    )
    op.create_index("ix_companies_name", "companies", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["company_id"], ["companies.id"], name="fk_users_company_id_companies", ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_company_id", "users", ["company_id"], unique=False)

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", task_status, server_default="NEW", nullable=False),
        sa.Column("priority", task_priority, server_default="MEDIUM", nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name="fk_tasks_owner_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_tasks"),
    )
    op.create_index("ix_tasks_status", "tasks", ["status"], unique=False)
    op.create_index("ix_tasks_priority", "tasks", ["priority"], unique=False)
    op.create_index("ix_tasks_owner_id", "tasks", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_table("tasks")
    op.drop_table("users")
    op.drop_table("companies")
    bind = op.get_bind()
    task_priority.drop(bind, checkfirst=True)
    task_status.drop(bind, checkfirst=True)
    company_mode.drop(bind, checkfirst=True)

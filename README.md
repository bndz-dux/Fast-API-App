# To-dos Application

FastAPI + Uvicorn + SQLAlchemy 2 + Alembic + PostgreSQL, with JWT authentication and role-based authorization.

## Project structure

```
app/
  core/        config (env settings), security (bcrypt, JWT), domain exceptions
  db/          declarative Base + timestamps, engine/session, get_db dependency
  models/      SQLAlchemy models: Company, User, Task
  schemas/     Pydantic request/response models (validation)
  services/    database queries & business rules
  api/
    deps.py    dependencies: DB session, current user, admin guard, pagination
    routes/    auth, users, companies, tasks
  main.py      FastAPI app, exception handler, routers
  initial_data.py  creates the first admin
alembic/       migrations
tests/         API tests (SQLite in-memory)
```

Relationships: `Company 1 — n User`, `User 1 — n Task`.

## Run

```bash
docker compose up -d                 # PostgreSQL
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env               # then set JWT_SECRET_KEY and FIRST_ADMIN_*
alembic upgrade head
python -m app.initial_data           # create admin
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs (use **Authorize** with username/email + password).

Tests: `pytest`

## API (`/api/v1`)

| Method | Path | Access |
| --- | --- | --- |
| POST | `/auth/login` | public (OAuth2 password form, returns JWT) |
| POST | `/auth/register` | public (creates regular user) |
| GET / PATCH | `/users/me` | authenticated |
| PUT | `/users/me/password` | authenticated |
| GET / POST | `/users` | admin |
| GET / PATCH / DELETE | `/users/{id}` | admin |
| GET | `/companies`, `/companies/{id}` | authenticated |
| POST / PATCH / DELETE | `/companies`, `/companies/{id}` | admin |
| GET / POST | `/tasks` | authenticated (users: own tasks, admin: all) |
| GET / PATCH / DELETE | `/tasks/{id}` | owner or admin |

List endpoints support `skip`, `limit` (max 100), `search`, and filters (`status`, `priority`, `owner_id`, `mode`, `company_id`, `is_active`).

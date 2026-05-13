# Task Management API

A FastAPI application with JWT auth, RBAC, pagination, filtering, and API versioning.

## Tech stack
- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **Alembic** — database migrations
- **PostgreSQL** — database
- **JWT** — authentication
- **bcrypt** — password hashing
- **pytest** — testing

## Local setup

```bash
# 1. clone and install
git clone https://github.com/jayachandra116/task-management.git
cd task_management-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. configure environment
cp .env.example .env
# fill in .env values

# 3. run migrations
alembic upgrade head

# 4. seed admin
python -m scripts.seed_admin

# 5. start
uvicorn app.main:app --reload
```

## API endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /api/v1/auth/register | ❌ | Register new user |
| POST | /api/v1/auth/login | ❌ | Login, get JWT token |
| GET | /api/v1/users/me | ✅ | Own profile |
| PATCH | /api/v1/users/me/password | ✅ | Change password |
| GET | /api/v1/users/ | ✅ admin | List all users |
| GET | /api/v1/user/{user_id} | ✅ admin | Get user details |
| PATCH | /api/v1/user/{user_id}/role | ✅ admin | Update user role |
| DELETE | /api/v1/user/{user_id} | ✅ admin | Delete user |
| POST | /api/v1/tasks/ | ✅ | Create task |
| GET | /api/v1/tasks/ | ✅ | List tasks |
| GET | /api/v1/tasks/{id} | ✅ | Get task |
| PATCH | /api/v1/tasks/{id} | ✅ | Update task |
| DELETE | /api/v1/tasks/{id} | ✅ | Delete task |

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key |
| `ALGORITHM` | ✅ | JWT algorithm, default HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | Token expiry, default 30 |
| `FIRST_ADMIN_EMAIL` | ✅ | Initial admin email |
| `FIRST_ADMIN_PASSWORD` | ✅ | Initial admin password |
| `POSTGRES_USER` | ✅ | PostgreSQL username |
| `POSTGRES_PASSWORD` | ✅ | PostgreSQL password |
| `POSTGRES_DB` | ✅ | PostgreSQL database name |
| `POSTGRES_SERVER` | ✅ | PostgreSQL host, default localhost |
| `POSTGRES_PORT` | ✅ | PostgreSQL port, default 5432 |

## Common errors

| Error | Fix |
|-------|-----|
| `relation "users" does not exist` | Run `alembic upgrade head` |
| `type "userrole" does not exist` | Enum not created — check migration |
| `KeyError: access_token` in tests | Routes not registered — check `main.py` |
| `ModuleNotFoundError: app` | Run from project root with `python -m` |
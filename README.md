# Booksmart Backend

Backend API built with FastAPI + SQLAlchemy + Alembic + MySQL.

## Requirements

- Python 3.10+
- MySQL 8+

## Local setup

1) Create and activate virtual environment

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Create local MySQL database and user

```sql
CREATE DATABASE IF NOT EXISTS booksmart CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'booksmart_user'@'localhost' IDENTIFIED BY 'booksmart_pass';
GRANT ALL PRIVILEGES ON booksmart.* TO 'booksmart_user'@'localhost';
FLUSH PRIVILEGES;
```

4) Configure `.env`

Use at least:

```env
DATABASE_URL=mysql+pymysql://booksmart_user:booksmart_pass@localhost:3306/booksmart
SECRET_KEY=replace_with_a_secure_random_key
```

Optional Sentry variables:

```env
SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>
SENTRY_ENVIRONMENT=development
SENTRY_RELEASE=booksmart@0.1.0
SENTRY_TRACES_SAMPLE_RATE=0.0
SENTRY_PROFILES_SAMPLE_RATE=0.0
SENTRY_SEND_DEFAULT_PII=false
```

If `SENTRY_DSN` is not set, Sentry stays disabled.

## Run database migrations

```bash
.venv/bin/python -m alembic upgrade head
```

## Run API

```bash
.venv/bin/uvicorn app.main:app --reload
```

- API root: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Authentication modes

### Normal mode (default)

- Use `/api/v1/auth/login/access-token` to get a JWT.
- Send `Authorization: Bearer <token>` on protected endpoints.
- WebSocket auth: `wss://your-domain.com/api/v1/ws?token=<JWT>`

### Local test mode (disable JWT checks)

For local DB/testing only:

```env
JWT_AUTH_DISABLED=true
JWT_BYPASS_USER_ID=1
JWT_BYPASS_ROLE_ID=3
JWT_BYPASS_NAME=Bypass
JWT_BYPASS_LASTNAME=User
JWT_BYPASS_EMAIL=bypass@booksmart.com
```

Notes:

- In this mode, HTTP endpoints that require authentication use a synthetic local user.
- WebSocket token validation is bypassed.
- Do not use this mode in production.

## WebSocket endpoint

- Endpoint: `/api/v1/ws`
- Normal mode: pass token as query param.
- Test mode (`JWT_AUTH_DISABLED=true`): token is optional.
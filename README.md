# CRM Platform

Full-stack CRM built from scratch to learn production-grade architecture.

## Stack

| Layer           | Technology                               |
| --------------- | ---------------------------------------- |
| Backend         | FastAPI (Python 3.12) + async SQLAlchemy |
| Database        | PostgreSQL 16 (JSONB, RLS, pg_trgm)      |
| Cache / Pub-Sub | Redis 7                                  |
| Background jobs | Celery + Celery Beat                     |
| Frontend        | Angular 20 (signals, standalone)         |
| State           | NgRx (store + signals)                   |
| Proxy           | Nginx                                    |
| Infrastrcuture  | Docker Compose                           |

## Project structure

```
crm-project/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Route handlers (thin layer)
│   │   ├── core/               # Config, security, dependencies
│   │   ├── db/                 # Session, base models, migrations
│   │   ├── domains/            # DDD modules
│   │   │   ├── iam/            # Users, roles, permissions
│   │   │   ├── objects/        # Object types, fields, records
│   │   │   ├── notifications/  # Audit log, notifications, bulk jobs
│   │   │   └── accounts/       # (Phase 3) Core CRM entities
│   │   └── workers/            # Celery tasks
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   └── src/app/
│       ├── core/               # Guards, interceptors, services
│       ├── features/           # Lazy-loaded feature modules
│       ├── layout/             # Shell, sidebar, header
│       └── store/              # NgRx state
├── nginx/
├── scripts/
├── docker-compose.yml
├── Makefile
└── .env.example
```

## Quick start

```bash
# 1. Clone and setup
cp .env.example .env

# 2. Start everything
make setup

# 3. Open in browser
open http://localhost          # Angular app
open http://localhost/api/docs # Swagger UI
```

## Development commands

```bash
make up               # Start all services
make down             # Stop all services
make logs             # Tail API + worker logs
make migrate          # Run pending migrations
make migrate create   # Generate new migration
make shell-api        # Bash in API container
make shell-db         # psql in Postgres container
```

## Build phases

| Phase | Scope                                            | Status |
| ----- | ------------------------------------------------ | ------ |
| 1     | Infrastrcuture, Docker, DB models, auth skeleton |        |
| 2     | Full IAM: users CRUD, roles, permissions         |        |
| 3     | Object engine: CRUD, dynamic fields, layouts     |        |
| 4     | Bulk imports with validation + progress via WS   |        |
| 5     | WebSockets: real-time notifications              |        |
| 6     | Chat module                                      |        |

## Architecture decisions

**Why JSONB for field values?**
Records store custom field values in a JSONB column (`data`). This avoids runtime
DDL changes when users add custom fields. Core searchable fields (name, owner,
stage) are prompted to native columns for indexed queries.

**Why UUID primary keys?**
Avoids sequential ID enumeration attacks and make distributed inserts after.

**Why three-layer permissions?**
JWT (authentication) -> Role permissions in JSONB (business rules) ->
PostgreSQL RLS (data isolation). Each layer catches what the previous one
might miss.

**Why Celery for bulk imports?**
Bulk csv processing can take minutes. Handling it in a bakground worker
keeps the API responsive and allows real-time progress reporting via
WebSockets.

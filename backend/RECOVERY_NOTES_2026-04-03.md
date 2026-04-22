# Backend Recovery Notes

Date: 2026-04-03

## Purpose

This document records the backend recovery work completed on 2026-04-03 to restore
application startup, fully remove the old external-auth remnants, and make the API
documentation available again at `http://localhost:8000/docs`.

## Main Problem

The backend was in a partially migrated state:

- Parts of the code still referenced an old external authentication implementation.
- Other parts had already moved toward local JWT authentication.
- Several core files no longer matched each other across domain models, repositories,
  dependency wiring, and database models.
- The FastAPI application could not import successfully, so the server never started and `/docs`
  could not load.

## Changes Made

### 1. Rebuilt user identity around local auth

Files:

- `src/mano/domain/models/user.py`
- `src/mano/application/dtos/user_dtos.py`
- `src/mano/application/use_cases/user_use_cases.py`
- `src/mano/domain/repositories/user_repository.py`
- `src/mano/domain/services/user_service.py`
- `src/mano/infrastructure/repositories/sqlalchemy_user_repository.py`

What changed:

- Standardized the backend around `auth_user_id`.
- Added `UserAuthId` as the main auth identity value object.
- Restored a consistent `UserProfile` model shape.
- Fixed the dataclass construction problems that were preventing module import.
- Updated DTOs, use cases, service logic, and repository mapping to use the same identity field.

Why:

- The codebase had conflicting assumptions about which auth identifier field should be used.
- That mismatch caused import errors, bad repository lookups, and broken route behavior.
- A single identity model was required to bring the backend back into a working state.

### 2. Restored local auth contracts and exception definitions

Files:

- `src/mano/domain/repositories/auth_repository.py`
- `src/mano/domain/exceptions/base.py`

What changed:

- Replaced the old auth repository contract with the local credential and password reset contract
  actually used by the auth service.
- Added missing domain exceptions:
  - `EmailAlreadyRegisteredError`
  - `InvalidPasswordResetTokenError`
  - `AvailabilityNotFoundError`

Why:

- Auth routes and services were importing exceptions and repository methods that no longer existed in
  the current code.
- Without these definitions, the application failed during import before FastAPI could start.

### 3. Rebuilt dependency injection for local auth

Files:

- `src/mano/dependencies.py`
- `src/mano/infrastructure/factories.py`

What changed:

- Removed the broken dependency path that imported the deleted external auth client.
- Added working providers for:
  - auth repository
  - auth service
  - auth use cases
  - user service
  - category service
  - availability service
  - review service
  - rating service
- Reworked `get_current_user` to decode the local JWT token and provision demo/local users when
  needed.

Why:

- The previous dependency graph referenced missing files and missing factory methods.
- FastAPI could not construct route dependencies, and startup failed immediately.

### 4. Restored ORM models to match the local auth migration

Files:

- `src/mano/infrastructure/database/models.py`

What changed:

- Restored `UserProfileModel` to include only `auth_user_id`.
- Added missing ORM models for:
  - `AuthCredentialModel`
  - `PasswordResetTokenModel`
- Cleaned relationships so the local auth repository and migrations align with the ORM.

Why:

- The repository layer already expected local auth tables, but the ORM file did not define them.
- The migration history also indicated the backend had already moved toward local auth storage.

### 5. Fixed FastAPI application startup

Files:

- `src/mano/main.py`

What changed:

- Removed the invalid `smtp_url=` argument from the `FastAPI(...)` constructor.
- Kept the docs routes and app wiring intact.
- Preserved health route, router registration, structured logging, and lifespan behavior.

Why:

- `FastAPI` does not accept `smtp_url` as an initialization parameter.
- Even after auth fixes, this would still have caused application startup failure.

### 6. Hardened settings loading for local development

Files:

- `src/mano/infrastructure/config/settings.py`

What changed:

- Allowed settings to read both `.env` and `../.env`.
- Added `DATABASE_URL` support as an override for the database connection string.
- Made nested settings classes read the same env files as the top-level settings object.
- Normalized legacy `DEBUG` shell values such as `DEBUG=release`.

Why:

- The backend was being run from `backend/`, but the main `.env` file is in the repo root.
- The shell environment also contained `DEBUG=release`, which broke strict boolean parsing.
- Without this change, the app could still fail before startup or target the wrong database host.

## Verification Performed

Verified on 2026-04-03:

- FastAPI app imports successfully.
- OpenAPI schema builds successfully.
- `/docs`, `/redoc`, `/openapi.json`, and `/health` are registered on the app.
- The repaired files pass `ruff` checks for `E` and `F` rules.
- User domain tests passed after the recovery changes.

## Important Environment Note

At verification time, there was no PostgreSQL listener on `localhost:5434`.

This means:

- The backend code is now able to start and serve API docs.
- Database-backed endpoints still require the local database to be running.

## Why This Recovery Was Done This Way

The goal was not to patch only the first error. The goal was to restore a professional, internally
consistent backend path.

The recovery therefore focused on:

- making imports stable
- removing deleted external-auth dependencies
- aligning auth, domain, repository, and ORM layers
- preserving compatibility where practical
- getting Swagger/OpenAPI working again without introducing another mixed-auth state

## Remaining Follow-Up Recommendations

- Run the backend with the local database running and re-test protected routes.
- Continue removing old terminology from historical notes if those notes are kept long term.
- Add a dedicated backend architecture note describing the final auth model so future recovery work is easier.

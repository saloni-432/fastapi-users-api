# FastAPI User CRUD API

[![Tests](https://github.com/saloni-432/fastapi-users-api/actions/workflows/tests.yml/badge.svg)](https://github.com/saloni-432/fastapi-users-api/actions/workflows/tests.yml)

[![Docker CI](https://github.com/saloni-432/fastapi-users-api/actions/workflows/docker-ci.yml/badge.svg)](https://github.com/saloni-432/fastapi-users-api/actions/workflows/docker-ci.yml)

A REST API built with FastAPI, PostgreSQL, Redis, Docker, and JWT-based authentication.

## 🔗 Links

- **GitHub:** :contentReference[oaicite:0]{index=0}

## Features

- User CRUD operations
- PostgreSQL database with SQLAlchemy ORM
- Redis caching for faster API responses
- Dockerized local development setup
- Pydantic request validation
- Background tasks
- JWT authentication using `python-jose`
- Password hashing using bcrypt via `passlib`
- Access tokens and refresh tokens
- Refresh-token rotation
- Logout by invalidating the stored refresh token
- Protected routes using OAuth2 Bearer tokens
- Role-based access control: `user` and `admin`
- API documentation through Swagger UI
- Automated tests with GitHub Actions
- Deployed on Railway

## Authentication flow

1. Send username and password to `POST /auth/token`.
2. The API returns an access token and a refresh token.
3. Use the access token as a Bearer token for protected endpoints.
4. Send the refresh token to `POST /auth/refresh` to receive a rotated token pair.
5. Call `POST /auth/logout` to invalidate the current refresh token.

> Current learning implementation: refresh-token hashes are stored in an in-memory fake user store. They reset when the application container restarts. The next planned improvement is persisting roles and refresh-token hashes in PostgreSQL.

## Run locally

```bash
docker compose up --build
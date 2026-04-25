# FastAPI User CRUD API

A production-ready REST API built with FastAPI, PostgreSQL and Docker.

## 🔗 Links
- **Live API:** https://fastapi-users-api-production.up.railway.app
- **API Docs:** https://fastapi-users-api-production.up.railway.app/docs
- **GitHub:** https://github.com/saloni-432/fastapi-users-api

## Features
- User CRUD operations
- PostgreSQL database
- Dockerized setup
- Pydantic validation
- SQLAlchemy ORM
- JWT Authentication (PyJWT + passlib)
- Background tasks
- Deployed on Railway.app

## Run locally
```bash
docker compose up --build
```
Open: http://localhost:8000/docs

## 🚀 Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/token` | Login, get JWT token | ❌ |
| GET | `/auth/me` | Get current user | ✅ |
| POST | `/auth/register-bg` | Register + background task | ✅ |
| GET | `/users` | List all users | ✅ |

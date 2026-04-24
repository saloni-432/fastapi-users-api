from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers import user_router, auth_router

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

Base.metadata.create_all(bind=engine)

# ── Rate limiter setup ──────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Existing router ─────────────────────────────────────────
app.include_router(user_router.router)
app.include_router(auth_router.router)  
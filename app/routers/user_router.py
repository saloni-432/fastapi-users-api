from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.crud import user_crud
from app.schemas.user_schemas import UserCreate, UserUpdate
import redis, json

redis_client = redis.Redis(host='localhost', port=6379, db=0)
router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user = user_crud.create_user(db, user)
    redis_client.delete("users:all")
    return user

@router.get("/")
def get_users(db: Session = Depends(get_db)):
    try:
       cached_users = redis_client.get("users:all")
    except Exception:
        cached_users = None
    
    if cached_users:
        return {
            "cached": True,
            "data": json.loads(cached_users)
        }
    
    users = user_crud.get_users(db)
    users_data = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
    redis_client.setex("users:all", 3600, json.dumps(users_data))
    return {
        "cached": False,
        "data": users_data
    }

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    try:
         cached_user = redis_client.get(f"user:{user_id}")
    except Exception:
        cached_user = None

    if cached_user:
        return {
            "cached": True,
            "data": json.loads(cached_user)
        }

    user = user_crud.get_user(db, user_id)

    if not user:
        return {"message": "User not found"}

    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }

    redis_client.setex(
        f"user:{user_id}",
        3600,
        json.dumps(user_data)
    )

    return {
        "cached": False,
        "data": user_data
    }

@router.put("/{user_id}")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    redis_client.delete("users:all")
    return user_crud.update_user(db, user_id, user)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    redis_client.delete("users:all")
    return user_crud.delete_user(db, user_id)
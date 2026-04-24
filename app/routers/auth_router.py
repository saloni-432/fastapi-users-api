from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import verify_password, create_access_token, get_current_user, fake_users

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    return {"username": current_user["username"]}

def send_welcome_email(username: str):
    import logging, time
    time.sleep(2)
    logging.info(f"Welcome email sent to {username}")

@router.post("/register-bg")
async def register_with_bg(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):
    background_tasks.add_task(send_welcome_email, current_user["username"])
    return {"message": "Registered! Email sending in background."}
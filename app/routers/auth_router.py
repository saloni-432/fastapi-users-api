from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

from app.auth import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    fake_users,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.get("/health")
async def auth_health():
    return {"message": "Auth router is working"}



@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm calls this field "username".
    # In a database project, you could use email here instead.
    user = fake_users.get(form_data.username)

    if user is None or not verify_password(
        form_data.password,
        user["hashed_password"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    # Store only the HASH of the refresh token.
    user["refresh_token_hash"] = hash_password(refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh")
async def refresh_access_token(data: RefreshTokenRequest):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
    )

    try:
        payload = jwt.decode(
            data.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")
        token_type = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = fake_users.get(username)

    if user is None:
        raise credentials_exception

    stored_refresh_token_hash = user.get("refresh_token_hash")

    if (
        stored_refresh_token_hash is None
        or not verify_password(data.refresh_token, stored_refresh_token_hash)
    ):
        raise credentials_exception

    # Refresh-token rotation:
    # the previous refresh token becomes invalid immediately.
    new_access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)
    user["refresh_token_hash"] = hash_password(new_refresh_token)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    # This invalidates the stored refresh token.
    # Existing access tokens remain usable until their 15-minute expiry.
    current_user["refresh_token_hash"] = None

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "role": current_user["role"],
    }


@router.get("/admin-only")
async def admin_only(current_user: dict = Depends(require_admin)):
    return {
        "message": "Welcome, admin",
        "username": current_user["username"],
    }
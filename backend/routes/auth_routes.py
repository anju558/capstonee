from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta

from backend.database import users_collection
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------
# SIGNUP
# ---------------------------
@router.post("/signup")
async def signup(email: str, password: str, role: str = "user"):
    if await users_collection.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="User already exists")

    await users_collection.insert_one({
        "email": email,
        "password": hash_password(password),
        "role": role,
        "refresh_token": None
    })

    return {"message": "User registered successfully"}


# ---------------------------
# LOGIN (Swagger-compatible)
# ---------------------------
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    refresh_token = create_refresh_token({"sub": user["email"]})

    await users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"refresh_token": refresh_token}}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ---------------------------
# REFRESH TOKEN
# ---------------------------
@router.post("/refresh")
async def refresh(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        user = await users_collection.find_one({
            "email": email,
            "refresh_token": refresh_token
        })

        if not user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token({
            "sub": email,
            "role": user["role"]
        })

        return {"access_token": new_access_token}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

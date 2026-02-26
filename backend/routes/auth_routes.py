import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId

from backend.database import users_collection, extension_codes_collection
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from backend.models import UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])


# =========================================================
# -------------------- SIGNUP -----------------------------
# =========================================================
@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):

    # Check if email already exists
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    await users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": user.role if hasattr(user, "role") else "user",
        "created_at": datetime.utcnow()
    })

    return {"message": "Signup successful"}


# =========================================================
# -------------------- LOGIN ------------------------------
# =========================================================
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = await users_collection.find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # ✅ CLEAN & CONSISTENT TOKEN STRUCTURE
    token = create_access_token({
        "sub": str(user["_id"]),      # Always user_id
        "email": user["email"],
        "role": user.get("role", "user")
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# =========================================================
# -------------------- ADMIN USERS ------------------------
# =========================================================
@router.get("/admin/users")
async def get_all_users(user=Depends(get_current_user)):

    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    users = await users_collection.find({}, {"password": 0}).to_list(1000)

    formatted_users = []
    for u in users:
        formatted_users.append({
            "id": str(u["_id"]),
            "username": u.get("username"),
            "email": u.get("email"),
            "role": u.get("role"),
            "created_at": u.get("created_at")
        })

    return formatted_users


# =========================================================
# ---------------- EXTENSION CONNECT ----------------------
# =========================================================
@router.post("/extension/connect")
async def extension_connect(user=Depends(get_current_user)):

    return {
        "status": "connected",
        "user_id": user["sub"]   # consistent
    }


# =========================================================
# ---------------- EXTENSION VERIFY -----------------------
# =========================================================
@router.post("/extension/verify")
async def extension_verify(code: str = Body(..., embed=True)):

    record = await extension_codes_collection.find_one({
        "code": code,
        "used": False
    })

    if not record:
        raise HTTPException(status_code=400, detail="Invalid code")

    if record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code expired")

    await extension_codes_collection.update_one(
        {"_id": record["_id"]},
        {"$set": {"used": True}}
    )

    # ✅ Same structure as login
    token = create_access_token({
        "sub": str(record["user_id"]),
        "role": "user"
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
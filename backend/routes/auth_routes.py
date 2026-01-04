from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.database import users_collection
from backend.auth import hash_password, verify_password, create_access_token
from backend.models import UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", status_code=201)
async def signup(user: UserCreate):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    await users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "role": "user"
    })

    return {"message": "Signup successful"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")

    token = create_access_token({
        "sub": user["email"],
        "role": user["role"],
        "_id": str(user["_id"])
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

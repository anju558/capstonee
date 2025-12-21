# backend/routes.py
from fastapi import APIRouter, Body, HTTPException, Depends, status
from typing import List, Optional
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import re

from backend.models import (
    Skill, SkillCreate, SkillUpdate,
    UserCreate, UserLogin, Token,
    UserSkillProfile
)
from backend.database import (
    skills_collection, users_collection, user_skills_collection
)
from backend.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user
)

router = APIRouter()

# --- Health Check ---
@router.get("/")  # Don't show in Swagger
def root_root():
    return {"status": "ok", "message": "Skill Agent Backend is running"}


# --- AUTH ---
# --- AUTH ---
@router.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    try:
        # 🔹 Validate confirm_password match (if model doesn't enforce it)
        if hasattr(user, 'confirm_password') and user.password != user.confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Passwords do not match"
            )

        # 🔹 Enforce password strength (if not done in Pydantic model)
        try:
            from backend.auth import validate_password_strength
            validate_password_strength(user.password)
        except ValueError as ve:
            raise HTTPException(
                status_code=400,
                detail=str(ve)
            )

        # 🔹 Check email uniqueness
        if await users_collection.find_one({"email": user.email}):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # 🔹 Check username (if model has it)
        username = getattr(user, 'username', None)
        if username:
            # Normalize & validate
            if not (3 <= len(username) <= 30):
                raise HTTPException(
                    status_code=400,
                    detail="Username must be 3–30 characters"
                )
            if not re.match(r"^[a-zA-Z0-9_]+$", username):
                raise HTTPException(
                    status_code=400,
                    detail="Username can only contain letters, numbers, and underscores"
                )
            if await users_collection.find_one({"username": username.lower()}):
                raise HTTPException(
                    status_code=400,
                    detail="Username already taken"
                )

        # 🔹 Hash & insert
        hashed_pw = get_password_hash(user.password)
        insert_data = {
            "email": user.email,
            "password": hashed_pw,
            "created_at": datetime.now(timezone.utc)
        }
        if username:
            insert_data["username"] = username.lower()

        result = await users_collection.insert_one(insert_data)

        token = create_access_token({"sub": str(result.inserted_id)})
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to register user. Please try again."
        ) from e


@router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    try:
        db_user = await users_collection.find_one({"email": user.email})
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        token = create_access_token({"sub": str(db_user["_id"])})
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Authentication service temporarily unavailable."
        ) from e


# --- GLOBAL SKILLS (Taxonomy Management) ---
@router.post("/skills", response_model=Skill, dependencies=[Depends(get_current_user)])
async def create_skill(skill: SkillCreate):
    try:
        data = jsonable_encoder(skill)
        result = await skills_collection.insert_one(data)
        created_skill = await skills_collection.find_one({"_id": result.inserted_id})
        if not created_skill:
            raise HTTPException(
                status_code=500,
                detail="Skill created but could not be retrieved."
            )
        return created_skill

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to create skill. Please check input and try again."
        ) from e


@router.get("/skills", response_model=List[Skill])
async def list_skills(category: Optional[str] = None):
    try:
        query = {"category": category} if category else {}
        skills = await skills_collection.find(query).to_list(100)
        return skills
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve skills."
        ) from e


@router.get("/skills/{id}", response_model=Skill)
async def get_skill(id: str):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(
                status_code=400,
                detail="Invalid skill ID format. Must be a 24-character hex string."
            )
        skill = await skills_collection.find_one({"_id": ObjectId(id)})
        if not skill:
            raise HTTPException(
                status_code=404,
                detail="Skill not found"
            )
        return skill

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error retrieving skill."
        ) from e


@router.put("/skills/{id}", response_model=Skill, dependencies=[Depends(get_current_user)])
async def update_skill(id: str, skill: SkillUpdate):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(
                status_code=400,
                detail="Invalid skill ID format."
            )
        update_data = {k: v for k, v in skill.dict().items() if v is not None}
        result = await skills_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Skill not found"
            )
        updated_skill = await skills_collection.find_one({"_id": ObjectId(id)})
        return updated_skill

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to update skill."
        ) from e


@router.delete("/skills/{id}", dependencies=[Depends(get_current_user)])
async def delete_skill(id: str):
    try:
        if not ObjectId.is_valid(id):
            raise HTTPException(
                status_code=400,
                detail="Invalid skill ID format."
            )
        result = await skills_collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Skill not found"
            )
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete skill."
        ) from e


# --- USER SKILL PROFILE (Dynamic Scoring) ---
@router.get("/profile/skills", response_model=UserSkillProfile, dependencies=[Depends(get_current_user)])
async def get_user_skill_profile(current_user: dict = Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        profile = await user_skills_collection.find_one({"user_id": user_id})
        if not profile:
            now = datetime.now(timezone.utc).isoformat()
            return UserSkillProfile(user_id=user_id, skills=[], updated_at=now)
        return UserSkillProfile(**profile)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve skill profile."
        ) from e


@router.post("/profile/skills", response_model=UserSkillProfile, dependencies=[Depends(get_current_user)])
async def update_user_skill_profile(
    profile_in: UserSkillProfile = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        user_id = str(current_user["_id"])
        now = datetime.now(timezone.utc).isoformat()

        # Enforce ownership
        if profile_in.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: Cannot update another user's profile."
            )

        profile_in.user_id = user_id
        profile_in.updated_at = now

        await user_skills_collection.update_one(
            {"user_id": user_id},
            {"$set": profile_in.dict()},
            upsert=True
        )

        updated = await user_skills_collection.find_one({"user_id": user_id})
        if not updated:
            raise HTTPException(
                status_code=500,
                detail="Profile update succeeded but retrieval failed."
            )
        return UserSkillProfile(**updated)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to update skill profile."
        ) from e
    

# --- REAL-TIME SKILL GAP DETECTION (WebSocket) ---
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime, timezone

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

manager = ConnectionManager()

@router.websocket("/events")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time skill gap detection.
    Input: { "user_id": "U1", "skill": "Excel Data Lookup", "errors": 2, "time_taken_sec": 35 }
    Output: Skill profile updated + gap alert.
    """
    await websocket.accept()
    user_id = "anonymous"

    try:
        while True:
            data = await websocket.receive_text()
            try:
                event = json.loads(data)
                user_id = event.get("user_id", "anonymous")
                
                # Validate required fields
                if not event.get("skill") or event.get("time_taken_sec") is None:
                    await websocket.send_text(json.dumps({"error": "Missing skill or time_taken_sec"}))
                    continue

                # 🔹 STEP 1: Find global skill definition
                skill_name = event["skill"]
                global_skill = await skills_collection.find_one({"name": skill_name})
                if not global_skill:
                    # Try category-based match (fallback)
                    global_skill = await skills_collection.find_one({"category": skill_name})
                    if not global_skill:
                        await websocket.send_text(json.dumps({"warning": f"Skill '{skill_name}' not in taxonomy"}))
                        continue

                # 🔹 STEP 2: Get or create user skill profile
                profile = await user_skills_collection.find_one({"user_id": user_id})
                if not profile:
                    # Initialize from global taxonomy
                    new_skills = []
                    for sub in global_skill.get("sub_skills", []):
                        sub_skills = []
                        for micro in sub.get("micro_skills", []):
                            sub_skills.append({
                                "name": micro["name"],
                                "description": micro.get("description"),
                                "score": micro.get("score", 50),
                                "last_updated": datetime.now(timezone.utc).isoformat()
                            })
                        new_skills.append({
                            "name": sub["name"],
                            "description": sub.get("description"),
                            "micro_skills": sub_skills
                        })
                    profile = {
                        "user_id": user_id,
                        "skills": new_skills,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    await user_skills_collection.insert_one(profile)

                # 🔹 STEP 3: Detect gap & update scores
                updated_skills = []
                gap_detected = False

                for sub_skill in profile["skills"]:
                    updated_micro = []
                    for micro in sub_skill["micro_skills"]:
                        # Simple heuristic: errors & time reduce score
                        # Base score: 50 → -5 per error, -2 per 5s over base
                        base_time = 20  # seconds (adjust per skill later)
                        time_penalty = max(0, event["time_taken_sec"] - base_time) * 0.4
                        error_penalty = event["errors"] * 5
                        score_delta = -(time_penalty + error_penalty)
                        
                        new_score = max(0, min(100, micro["score"] + score_delta))
                        
                        # Detect significant gap
                        if micro["score"] >= 60 and new_score < 50:
                            gap_detected = True
                            print(f"⚠️ SKILL GAP DETECTED: {user_id} | {micro['name']} ({micro['score']} → {new_score})")

                        updated_micro.append({
                            "name": micro["name"],
                            "description": micro.get("description"),
                            "score": int(new_score),
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        })
                    updated_skills.append({
                        "name": sub_skill["name"],
                        "description": sub_skill.get("description"),
                        "micro_skills": updated_micro
                    })

                # 🔹 STEP 4: Upsert updated profile
                await user_skills_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "skills": updated_skills,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    upsert=True
                )

                # 🔹 STEP 5: Respond
                response = {
                    "status": "gap_detected" if gap_detected else "updated",
                    "user_id": user_id,
                    "skill": skill_name,
                    "gap_detected": gap_detected,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                await websocket.send_text(json.dumps(response))

            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                print(f"⚠️ Event processing error: {e}")
                await websocket.send_text(json.dumps({"error": "Processing failed"}))

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(user_id)
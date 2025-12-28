# backend/models.py
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, field_serializer
from bson import ObjectId
import re

# --- Custom ObjectId for Pydantic v2 ---
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

# --- Global Skill Taxonomy ---
class MicroSkill(BaseModel):
    name: str
    description: Optional[str] = None
    score: int = Field(0, ge=0, le=100)

class SubSkill(BaseModel):
    name: str
    description: Optional[str] = None
    micro_skills: List[MicroSkill] = []

class Skill(BaseModel):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    name: str
    category: str
    sub_skills: List[SubSkill] = []

    model_config = {"populate_by_name": True}

    @field_serializer("id", when_used="json")
    def serialize_id(self, v: Optional[PyObjectId]) -> Optional[str]:
        return str(v) if v else None

class SkillCreate(BaseModel):
    name: str
    category: str
    sub_skills: List[SubSkill] = []

class SkillUpdate(BaseModel):
    name: Optional[str]
    category: Optional[str]
    sub_skills: Optional[List[SubSkill]]

# --- Auth Models (Pydantic v2 with validation) ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="3–30 chars: letters, numbers, underscores")
    email: EmailStr
    password: str = Field(..., min_length=8, description="Min 8 chars, 1 upper, 1 lower, 1 digit, 1 special (!@#$%^&*)")
    confirm_password: str = Field(..., min_length=8)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character (e.g., !, @, #)")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- DYNAMIC USER SKILL PROFILE ---
class MicroSkillScore(BaseModel):
    name: str
    description: Optional[str] = None
    score: int = Field(0, ge=0, le=100)
    last_updated: Optional[str] = None

class SubSkillScore(BaseModel):
    name: str
    description: Optional[str] = None
    micro_skills: List[MicroSkillScore] = []

class UserSkillProfile(BaseModel):
    user_id: str
    skills: List[SubSkillScore] = []
    updated_at: str

# --- Task Event Model ---
class TaskEvent(BaseModel):
    user_id: str  # MongoDB _id string
    skill: str    # e.g., "Excel Data Lookup"
    errors: int = 0
    retries: int = 0
    time_taken_sec: float
    timestamp: Optional[str] = None
    task_id: Optional[str] = None
    success: Optional[bool] = None

    class Config:
        populate_by_name = True

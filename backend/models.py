from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, field_serializer
from bson import ObjectId
import re
from datetime import datetime


# -------------------------------------------------
# 🔹 Custom ObjectId for Pydantic v2
# -------------------------------------------------
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


# -------------------------------------------------
# 📚 Skill Taxonomy Models
# -------------------------------------------------
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
    def serialize_id(self, v):
        return str(v) if v else None


# -------------------------------------------------
# 👤 Auth Models
# -------------------------------------------------
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    role: str = "user"  # 👈 Added role support

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only letters, numbers, underscore")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ["user", "admin"]:
            raise ValueError("Role must be 'user' or 'admin'")
        return v


class Token(BaseModel):
    access_token: str
    token_type: str


# -------------------------------------------------
# 🧠 Persistent Skill State (CORE)
# -------------------------------------------------
class UserSkillState(BaseModel):
    user_id: str
    skill: str
    current_level: int = Field(..., ge=1, le=5)
    target_level: int = Field(5, ge=1, le=5)
    confidence_score: float = Field(0.0, ge=0.0, le=1.0)
    last_evaluated: datetime

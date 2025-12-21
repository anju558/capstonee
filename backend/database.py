# backend/database.py
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "skill_taxonomy_v2")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is not set in environment variables.")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db["users"]
skills_collection = db["skills"]
user_skills_collection = db["user_skills"]  # For dynamic per-user profiles
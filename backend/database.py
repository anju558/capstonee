import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReadPreference
from dotenv import load_dotenv

# Ensure env vars are available even if imported elsewhere
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not set in .env")

if not DB_NAME:
    raise RuntimeError("❌ DB_NAME not set in .env")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=8000,
    read_preference=ReadPreference.PRIMARY_PREFERRED,
    retryWrites=True
)

database = client[DB_NAME]

# Collections
users_collection = database["users"]
skills_collection = database["skills"]
user_skills_collection = database["user_skills"]
events_collection = database["events"]
knowledge_collection = database["skill_knowledge"]

# -------------------------------------------------
# ✅ SAFE MongoDB initialization
# -------------------------------------------------
async def init_db():
    try:
        await client.server_info()
        await users_collection.create_index("email", unique=True)
        await skills_collection.create_index("skill_name", unique=True)
        await events_collection.create_index("user_id")
        print("✅ MongoDB connection verified & indexes ensured")
    except Exception as e:
        print(f"⚠️ MongoDB not ready yet: {e}")
        raise

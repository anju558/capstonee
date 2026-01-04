import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReadPreference

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=8000,
    read_preference=ReadPreference.PRIMARY_PREFERRED,
    retryWrites=True
)

db = client[DB_NAME]

# Collections
users_collection = db["users"]
skills_collection = db["skills"]
user_skills_collection = db["user_skills"]
events_collection = db["events"]

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

import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReadPreference
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not set")

if not DB_NAME:
    raise RuntimeError("❌ DB_NAME not set")

client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=8000,
    read_preference=ReadPreference.PRIMARY_PREFERRED,
    retryWrites=True
)

database = client[DB_NAME]

# -------------------- Collections --------------------
users_collection = database["users"]
skills_collection = database["skills"]
user_skills_collection = database["user_skills"]
user_skill_state_collection = database["user_skill_state"]
events_collection = database["events"]
knowledge_collection = database["skill_knowledge"]

# 🔑 EXTENSION AUTO-LOGIN
extension_codes_collection = database["extension_codes"]

# ✅ ADD THIS (for dashboard graph history)
skill_history_collection = database["skill_history"]


# -------------------- Init --------------------
async def init_db():
    await client.server_info()

    await users_collection.create_index("email", unique=True)

    await user_skill_state_collection.create_index(
        [("user_id", 1), ("skill", 1)], unique=True
    )

    await events_collection.create_index("user_id")

    # ✅ Recommended index for graph performance
    await skill_history_collection.create_index("user_id")

    await knowledge_collection.create_index("embedding")

    print("✅ MongoDB ready")
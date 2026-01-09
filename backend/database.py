import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReadPreference
from dotenv import load_dotenv

# -------------------------------------------------
# 🔐 Load environment variables
# -------------------------------------------------
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI not set in .env")

if not DB_NAME:
    raise RuntimeError("❌ DB_NAME not set in .env")

# -------------------------------------------------
# 🔗 MongoDB Client
# -------------------------------------------------
client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=8000,
    read_preference=ReadPreference.PRIMARY_PREFERRED,
    retryWrites=True
)

database = client[DB_NAME]

# -------------------------------------------------
# 📦 Collections
# -------------------------------------------------
users_collection = database["users"]
skills_collection = database["skills"]
user_skills_collection = database["user_skills"]
user_skill_state_collection = database["user_skill_state"]
events_collection = database["events"]
knowledge_collection = database["skill_knowledge"]

# -------------------------------------------------
# 🚀 Safe MongoDB Initialization
# -------------------------------------------------
async def init_db():
    """
    - Verifies MongoDB connection
    - Creates required indexes safely
    """
    try:
        await client.server_info()

        # Users
        await users_collection.create_index(
            "email", unique=True, background=True
        )

        # Skill taxonomy
        await skills_collection.create_index(
            "skill_name", unique=True, background=True
        )

        # User skill state (core memory)
        await user_skill_state_collection.create_index(
            [("user_id", 1), ("skill", 1)],
            unique=True,
            background=True
        )

        # Events
        await events_collection.create_index("user_id", background=True)
        await events_collection.create_index("created_at", background=True)

        # Knowledge base
        await knowledge_collection.create_index("embedding", background=True)

        print("✅ MongoDB connection verified & indexes ensured")

    except Exception as e:
        print(f"❌ MongoDB initialization failed: {e}")
        raise

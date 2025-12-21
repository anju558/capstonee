# test_db.py
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_path = Path(".") / ".env"
print("🔍 Looking for .env at:", env_path.resolve())
load_dotenv(dotenv_path=env_path)

# Check vars
print("MONGO_URI:", "✅ set" if os.getenv("MONGO_URI") else "❌ missing")
print("JWT_SECRET_KEY:", "✅ 64 chars" if len(os.getenv("JWT_SECRET_KEY") or "") == 64 else f"⚠️ {len(os.getenv('JWT_SECRET_KEY') or '')} chars")

# Test DB
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME", "skill_taxonomy_v2")]
    collections = db.list_collection_names()
    print("✅ DB connected. Collections:", collections)
except Exception as e:
    print("❌ DB Error:", e)
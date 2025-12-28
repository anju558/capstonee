# test_db.py
from pathlib import Path
from dotenv import load_dotenv
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# -------------------------------------------------
# Load .env
# -------------------------------------------------
env_path = Path(".") / ".env"
print("Looking for .env at:", env_path.resolve())
load_dotenv(dotenv_path=env_path)

# -------------------------------------------------
# Check environment variables
# -------------------------------------------------
print("MONGO_URI:", "✅ set" if os.getenv("MONGO_URI") else "❌ missing")

jwt = os.getenv("JWT_SECRET_KEY") or ""
print(
    "JWT_SECRET_KEY:",
    "✅ 64 chars" if len(jwt) == 64 else f"⚠️ {len(jwt)} chars"
)

# -------------------------------------------------
# Async DB test
# -------------------------------------------------
async def test_db():
    try:
        client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("DB_NAME", "skill_taxonomy_v2")]

        collections = await db.list_collection_names()
        print("✅ DB connected successfully")
        print("📦 Collections:", collections)

        client.close()

    except Exception as e:
        print("❌ DB Error:", e)


if __name__ == "__main__":
    asyncio.run(test_db())

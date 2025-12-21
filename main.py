# main.py
import os
import sys
from pathlib import Path

# 🔐 MUST load .env BEFORE any backend.* imports
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"❌ .env not found at {env_path}", file=sys.stderr)
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path)

# Validate critical env vars
required = ["MONGO_URI", "JWT_SECRET_KEY"]
for key in required:
    if not os.getenv(key):
        print(f"❌ Missing {key} in .env", file=sys.stderr)
        sys.exit(1)
print("✅ .env loaded successfully")

# Now import FastAPI & routes
from fastapi import FastAPI
from backend.routes import router

app = FastAPI(
    title="Skill Agent Backend",
    description="Real-Time Skill Gap Detection & Upskilling"
)

app.include_router(router, prefix="/api")
import os
import sys
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv

# -------------------------------------------------
# 🔐 LOAD .env FIRST (BEFORE anything else)
# -------------------------------------------------
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print(f"❌ .env not found at {env_path}", file=sys.stderr)
    sys.exit(1)

load_dotenv(dotenv_path=env_path)
print("✅ .env loaded successfully")

# -------------------------------------------------
# ✅ Validate required environment variables
# -------------------------------------------------
required_vars = ["MONGO_URI", "DB_NAME", "JWT_SECRET_KEY"]
for var in required_vars:
    if not os.getenv(var):
        print(f"❌ Missing {var} in .env", file=sys.stderr)
        sys.exit(1)

# -------------------------------------------------
# 🚀 Create FastAPI app (ONLY ONCE)
# -------------------------------------------------
app = FastAPI(
    title="Skill Agent Backend",
    description="Real-Time Skill Gap Detection & Upskilling",
    version="1.0.0"
)

# -------------------------------------------------
# 🧠 Startup: Initialize MongoDB
# -------------------------------------------------
from backend.database import init_db

@app.on_event("startup")
async def startup_event():
    await init_db()

# -------------------------------------------------
# 🔗 Routes
# -------------------------------------------------
from backend.routes import router
app.include_router(router, prefix="/api")

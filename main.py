import sys
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv

# -------------------------------------------------
# 🔐 LOAD .env BEFORE ANY OTHER IMPORT
# -------------------------------------------------
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    print("❌ .env file not found")
    sys.exit(1)

load_dotenv(env_path)
print("✅ .env loaded successfully")

# -------------------------------------------------
# ✅ SAFE IMPORTS (after env is loaded)
# -------------------------------------------------
from backend.database import init_db
from backend.routes import router

app = FastAPI(
    title="Skill Agent Backend",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(router, prefix="/api")

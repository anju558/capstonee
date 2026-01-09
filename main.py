import sys
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (optional cleanup later)


app = FastAPI(
    title="Skill Agent Backend",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router, prefix="/api")

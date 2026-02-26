import sys
from pathlib import Path
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# -------------------------------------------------
# 🔐 LOAD .env BEFORE ANY OTHER IMPORT
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

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
    await init_db()
    yield


app = FastAPI(
    title="Skill Agent Backend",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------------------------------------
# 🔌 BACKEND ROUTES
# -------------------------------------------------
app.include_router(router, prefix="/api")

# -------------------------------------------------
# 🌐 FRONTEND CONFIGURATION
# -------------------------------------------------

frontend_path = BASE_DIR / "frontend"

# Serve ONLY static assets (CSS + JS)
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# -------------------------------------------------
# 🏠 FRONTEND PAGES
# -------------------------------------------------

@app.get("/")
async def home():
    return FileResponse(frontend_path / "index.html")

@app.get("/signup")
async def signup_page():
    return FileResponse(frontend_path / "signup.html")

@app.get("/login")
async def login_page():
    return FileResponse(frontend_path / "login.html")

@app.get("/download")
async def download_page():
    return FileResponse(frontend_path / "download.html")    

@app.get("/dashboard")
async def dashboard_page():
    return FileResponse(frontend_path / "dashboard.html")

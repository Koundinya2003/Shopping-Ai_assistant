import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database import init_db
from app.database.seed import seed
from app.api.products import router as products_router
from app.api.recommendations import router as recommendations_router

# ── Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

load_dotenv()

# ── Environment validation ────────────────────────────────────────────
REQUIRED_ENV_VARS = [
    "OPENROUTER_API_KEY",
]

missing = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing:
    logger.warning(
        "Missing required environment variables: %s. "
        "LLM features will be disabled until these are set.",
        ", ".join(missing),
    )

app = FastAPI(
    title="AI Grocery Assistant",
    description="Backend API for the AI-powered grocery shopping assistant",
    version="1.0.0",
)

# CORS configuration - restrict origins in production
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://localhost:8000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(products_router)
app.include_router(recommendations_router)


@app.on_event("startup")
def on_startup():
    """Initialize database and seed data on startup."""
    logger.info("Starting application startup...")
    init_db()
    seed()
    logger.info("Application startup complete.")


@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "AI Grocery Assistant",
    }

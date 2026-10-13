from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import logging

from .config import settings
from .routes.predict import router

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"=== {settings.app_name} Starting ===")
logger.info(f"Debug mode: {settings.debug}")
logger.info(f"CORS origins: {settings.cors_origins}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Log a confirmation once the application has started."""
    logger.info("=== Application started successfully ===")
    logger.info("API endpoint: /predict")
    logger.info(f"Allowed origins: {settings.cors_origins}")
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# Include routes FIRST
app.include_router(router)
logger.info("Routes registered")

# Mount frontend static files at root (after routes so API takes precedence)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
logger.info("Static files mounted")

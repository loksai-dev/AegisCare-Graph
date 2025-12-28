"""
FastAPI Main Application
AegisCare Graph - Explainable Clinical Decision Intelligence Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import router
from backend.config import settings, validate_settings
from backend.database import db
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate settings on startup
try:
    validate_settings()
    logger.info("Settings validated successfully")
except Exception as e:
    logger.error(f"Settings validation failed: {e}")
    raise

# Create FastAPI application
app = FastAPI(
    title="AegisCare Graph API",
    description="Explainable Clinical Decision Intelligence Platform using Neo4j",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        # Explicitly initialize the database connection
        db._connect()
        # Verify Neo4j connection
        db.execute_query("RETURN 1 as test")
        logger.info("Neo4j connection verified successfully")
    except Exception as e:
        logger.error(f"Failed to verify Neo4j connection: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    try:
        db.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AegisCare Graph API",
        "description": "Explainable Clinical Decision Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


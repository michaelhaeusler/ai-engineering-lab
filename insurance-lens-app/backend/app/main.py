"""Main FastAPI application for InsuranceLens backend."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes import health, policies


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.upload_folder)
    upload_dir.mkdir(exist_ok=True)
    
    # Initialize vector database connections here if needed
    # await initialize_qdrant()
    
    yield
    
    # Cleanup resources here if needed
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="InsuranceLens API",
        description="AI assistant for German health insurance policy understanding",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(policies.router, prefix="/api/v1")
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        if settings.debug:
            import traceback
            error_detail = traceback.format_exc()
        else:
            error_detail = "Internal server error"
            
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": error_detail}
        )
    
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

"""
main.py - FastAPI application entrypoint for WindScope.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.services.data_loader import load_datasets
from backend.app.routes import (
    health,
    summary,
    actuals,
    forecasts,
    accuracy,
    vintages,
    data_quality,
    risk
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload and cache datasets on startup
    print(f"Starting {settings.app_name}...")
    try:
        act, fc, rep = load_datasets()
        print(f"Preloaded {len(act)} actuals rows and {len(fc)} forecast rows.")
    except Exception as e:
        print(f"Warning: Failed to preload datasets in lifespan startup: {e}")
    yield
    print("Shutting down WindScope...")


app = FastAPI(
    title=settings.app_name,
    description="UK Wind Forecast Intelligence Platform for day-ahead electricity procurement.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Enable CORS for frontend Vite development and production deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    from fastapi.responses import JSONResponse
    tb = traceback.format_exc()
    print(f"Unhandled Exception: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb}
    )


# Mount all endpoint routers
app.include_router(health.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(actuals.router, prefix="/api")
app.include_router(forecasts.router, prefix="/api")
app.include_router(accuracy.router, prefix="/api")
app.include_router(vintages.router, prefix="/api")
app.include_router(data_quality.router, prefix="/api")
app.include_router(risk.router, prefix="/api")


@app.get("/api/docs", include_in_schema=False)
def api_docs():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title=f"{settings.app_name} — Docs")


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "docs": "/docs",
        "api_docs": "/api/docs",
        "health": "/api/health",
        "status": "operational"
    }

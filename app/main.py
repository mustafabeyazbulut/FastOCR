"""
FastAPI Ana Uygulama
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yasam dongusu"""
    import sys
    # Startup
    from app.services.pdf_service import default_pdf_service
    print("\nFastOCR API baslatildi", flush=True)
    print("Docs:   http://localhost:8000/docs", flush=True)
    print("Health: http://localhost:8000/api/v1/health\n", flush=True)
    yield
    # Shutdown
    print("Servis kapatildi", flush=True)


app = FastAPI(
    title="FastOCR API",
    description="PDF ve goruntu dosyalarindan OCR ile metin cikarma servisi.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["PDF Operations"])


@app.get("/")
async def root():
    return {
        "message": "FastOCR API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

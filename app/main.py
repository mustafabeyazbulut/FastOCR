"""
FastAPI Ana Uygulama
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router
import logging

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# FastAPI uygulaması
app = FastAPI(
    title="FastOCR API",
    description="PDF ve görüntü dosyalarından OCR ile metin çıkarma servisi. Tesseract ve EasyOCR desteği, Türkçe ve İngilizce dil desteği.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da spesifik domainler ayarlanmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları kaydet
app.include_router(router, prefix="/api/v1", tags=["PDF Operations"])


@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında çalışır"""
    logger.info("🚀 FastOCR API Servisi başlatılıyor...")
    
    # OCR motorunu kontrol et
    from app.services.pdf_service import default_pdf_service
    logger.info(f"✅ OCR motoru hazır! (Diller: {default_pdf_service.languages})")
    
    logger.info("✨ Servis kullanıma hazır!")
    logger.info("📖 API Dokümantasyonu: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapanırken çalışır"""
    logger.info("👋 Servis kapatılıyor...")


@app.get("/")
async def root():
    """Ana sayfa"""
    return {
        "message": "FastOCR API'ye hoş geldiniz!",
        "description": "PDF ve görüntü dosyalarından OCR ile metin çıkarma",
        "docs": "/docs",
        "health": "/api/v1/health",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

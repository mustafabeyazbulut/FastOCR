"""
API Endpoints
PDF işleme ve health check endpoint'leri
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.schemas import PDFProcessResponse, HealthResponse, PageData, FileInfo, ImageOCRResponse
from typing import Optional
import os
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Servis sağlık kontrolü
    
    Returns:
        HealthResponse: Servis durumu
    """
    from app.services.pdf_service import default_pdf_service
    return HealthResponse(
        status="healthy",
        ocr_ready=default_pdf_service.is_ready,
        version="1.0.0"
    )


@router.post("/upload-pdf", response_model=PDFProcessResponse)
async def upload_pdf(
    file: UploadFile = File(..., description="Yüklenecek PDF dosyası"),
    language: Optional[str] = Form("tr,en", description="OCR dil kodu (tr, en veya tr,en)")
):
    """
    PDF dosyası yükle ve OCR ile işle
    
    Args:
        file: PDF dosyası
        language: OCR için dil seçimi (tr=Türkçe, en=İngilizce, tr,en=Her ikisi)
    
    Returns:
        PDFProcessResponse: İşlenmiş PDF verisi
    """
    # Dosya uzantısı kontrolü
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Sadece PDF dosyaları yüklenebilir!"
        )
    
    # Geçici dosya kaydetme
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # UUID ile benzersiz dosya ismi oluştur
    import uuid
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = upload_dir / unique_filename
    
    try:
        # Dosyayı kaydet
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"📄 PDF dosyası kaydedildi: {file.filename}")
        
        # Dil ayarını güncelle
        languages = [lang.strip() for lang in language.split(",")]
        logger.info(f"🌐 Seçilen diller: {languages}")
        
        # Seçilen diller için PDFService oluştur
        from app.services.pdf_service import PDFService
        service = PDFService(languages=languages)
        
        # PDF'i işle
        result = await service.process_pdf(str(file_path))
        
        # Hata kontrolü
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=f"PDF işleme hatası: {result['error']}"
            )
        
        # Response formatla
        pages_list = []
        for page_num, content in sorted(result.get("pages", {}).items()):
            # Sayfa numarasını içeriğe ekle
            formatted_content = f"{page_num}. Sayfa:\n{content}"
            pages_list.append(PageData(
                page_number=page_num,
                content=formatted_content
            ))
        
        file_info = FileInfo(
            filename=result["file_info"]["filename"],
            size_bytes=result["file_info"]["size_bytes"],
            total_pages=result["total_pages"]
        )
        
        logger.info(f"✅ PDF başarıyla işlendi: {result['total_pages']} sayfa, {result['total_characters']} karakter")
        
        return PDFProcessResponse(
            success=True,
            message=f"PDF başarıyla işlendi! {result['total_pages']} sayfa, {result['total_characters']} karakter.",
            file_info=file_info,
            method=result["method"],
            pages=pages_list,
            total_characters=result["total_characters"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ İşlem hatası: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Beklenmeyen hata: {str(e)}"
        )
    
    finally:
        # Geçici dosyayı temizle
        if file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Geçici dosya silindi: {file.filename}")
            except Exception as e:
                logger.warning(f"⚠️ Dosya silinemedi: {e}")


@router.post("/upload-image", response_model=ImageOCRResponse)
async def upload_image(
    file: UploadFile = File(..., description="Yüklenecek görüntü dosyası (JPG, PNG, JPEG)"),
    language: Optional[str] = Form("tur+eng", description="OCR dil kodu (tur, eng veya tur+eng)")
):
    """
    Görüntü dosyası yükle ve OCR ile işle
    
    Args:
        file: Görüntü dosyası (JPG, PNG, JPEG)
        language: OCR için dil seçimi (tur=Türkçe, eng=İngilizce, tur+eng=Her ikisi)
    
    Returns:
        ImageOCRResponse: İşlenmiş görüntü verisi
    """
    # Dosya uzantısı kontrolü
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Sadece görüntü dosyaları yüklenebilir! Desteklenen: {', '.join(allowed_extensions)}"
        )
    
    # Geçici dosya kaydetme
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # UUID ile benzersiz dosya ismi oluştur
    import uuid
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = upload_dir / unique_filename
    
    try:
        # Dosyayı kaydet
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"📷 Görüntü dosyası kaydedildi: {file.filename}")
        
        # Dil ayarını güncelle
        ocr_language = language.replace(',', '+')  # tr,en -> tur+eng
        if 'tr' in language:
            ocr_language = ocr_language.replace('tr', 'tur')
        if 'en' in language:
            ocr_language = ocr_language.replace('en', 'eng')
        
        logger.info(f"🌐 Seçilen dil: {ocr_language}")
        
        # Servisi oluştur ve görüntüyü işle
        from app.services.pdf_service import PDFService
        
        # Dilleri liste olarak gönder (process_image için farklı format)
        service = PDFService(languages=[])  # Image için dil gerekmiyor
        
        # Görüntüyü işle
        result = await service.process_image(str(file_path), language=ocr_language)
        
        # Hata kontrolü
        if "error" in result:
            raise HTTPException(
                status_code=500,
                detail=f"Görüntü işleme hatası: {result['error']}"
            )
        
        logger.info(f"✅ Görüntü başarıyla işlendi: {result['total_characters']} karakter")
        
        return ImageOCRResponse(
            success=True,
            message=f"Görüntü başarıyla işlendi! {result['total_characters']} karakter.",
            file_info=result.get("file_info"),
            method=result["method"],
            text=result["text"],
            total_characters=result["total_characters"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ İşlem hatası: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Beklenmeyen hata: {str(e)}"
        )
    
    finally:
        # Geçici dosyayı temizle
        if file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"🗑️ Geçici dosya silindi: {file.filename}")
            except Exception as e:
                logger.warning(f"⚠️ Dosya silinemedi: {e}")

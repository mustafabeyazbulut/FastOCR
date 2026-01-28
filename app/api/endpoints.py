"""
API Endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import PDFProcessResponse, HealthResponse, PageData, FileInfo, ImageOCRResponse
import os
import shutil
from pathlib import Path
import uuid

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Servis saglik kontrolu"""
    from app.services.pdf_service import default_pdf_service
    return HealthResponse(
        status="healthy",
        ocr_ready=default_pdf_service.is_ready,
        version="1.0.0"
    )


@router.post("/upload-pdf", response_model=PDFProcessResponse)
async def upload_pdf(file: UploadFile = File(..., description="PDF dosyasi")):
    """
    PDF dosyasi yukle ve OCR ile isle
    Otomatik olarak Turkce ve Ingilizce destekler
    """
    print(f"\n[PDF] Istek geldi: {file.filename}", flush=True)

    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Sadece PDF dosyalari yuklenebilir!")

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        from app.services.pdf_service import PDFService
        service = PDFService()
        result = await service.process_pdf(str(file_path))

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"PDF isleme hatasi: {result['error']}")

        pages_list = []
        for page_num, content in sorted(result.get("pages", {}).items()):
            pages_list.append(PageData(
                page_number=page_num,
                content=f"{page_num}. Sayfa:\n{content}"
            ))

        print(f"[PDF] Cevap donduruldu: {result['total_pages']} sayfa, {result['total_characters']} karakter\n", flush=True)

        return PDFProcessResponse(
            success=True,
            message=f"PDF islendi: {result['total_pages']} sayfa, {result['total_characters']} karakter",
            file_info=FileInfo(
                filename=result["file_info"]["filename"],
                size_bytes=result["file_info"]["size_bytes"],
                total_pages=result["total_pages"]
            ),
            method=result["method"],
            pages=pages_list,
            total_characters=result["total_characters"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")
    finally:
        if file_path.exists():
            os.remove(file_path)


@router.post("/upload-image", response_model=ImageOCRResponse)
async def upload_image(file: UploadFile = File(..., description="Goruntu dosyasi (JPG, PNG)")):
    """
    Goruntu dosyasi yukle ve OCR ile isle
    Otomatik olarak Turkce ve Ingilizce destekler
    """
    print(f"\n[IMAGE] Istek geldi: {file.filename}", flush=True)

    allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Desteklenen formatlar: {', '.join(allowed_extensions)}")

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{uuid.uuid4()}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        from app.services.pdf_service import PDFService
        service = PDFService()
        result = await service.process_image(str(file_path))

        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Goruntu isleme hatasi: {result['error']}")

        print(f"[IMAGE] Cevap donduruldu: {result['total_characters']} karakter\n", flush=True)

        return ImageOCRResponse(
            success=True,
            message=f"Goruntu islendi: {result['total_characters']} karakter",
            file_info=result.get("file_info"),
            method=result["method"],
            text=result["text"],
            total_characters=result["total_characters"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")
    finally:
        if file_path.exists():
            os.remove(file_path)

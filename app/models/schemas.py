"""
Pydantic Şemaları
API request ve response modelleri
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PageData(BaseModel):
    """Tek sayfa verisi"""
    page_number: int = Field(..., description="Sayfa numarası")
    content: str = Field(..., description="Sayfa içeriği (OCR metni)")


class FileInfo(BaseModel):
    """PDF dosya bilgisi"""
    filename: str = Field(..., description="Dosya adı")
    size_bytes: int = Field(..., description="Dosya boyutu (byte)")
    total_pages: int = Field(..., description="Toplam sayfa sayısı")


class PDFProcessResponse(BaseModel):
    """PDF işleme cevabı"""
    success: bool = Field(..., description="İşlem başarılı mı?")
    message: str = Field(..., description="İşlem mesajı")
    file_info: Optional[FileInfo] = Field(None, description="Dosya bilgileri")
    method: Optional[str] = Field(None, description="Kullanılan yöntem (PyMuPDF veya EasyOCR)")
    pages: Optional[List[PageData]] = Field(None, description="Sayfa verileri listesi")
    total_characters: Optional[int] = Field(None, description="Toplam karakter sayısı")
    error: Optional[str] = Field(None, description="Hata mesajı (varsa)")


class HealthResponse(BaseModel):
    """Health check cevabı"""
    status: str = Field(..., description="Servis durumu")
    ocr_ready: bool = Field(..., description="OCR motoru hazır mı?")
    version: str = Field(..., description="API versiyonu")


class ImageOCRResponse(BaseModel):
    """Görüntü OCR cevabı"""
    success: bool = Field(..., description="İşlem başarılı mı?")
    message: str = Field(..., description="İşlem mesajı")
    file_info: Optional[dict] = Field(None, description="Dosya bilgileri")
    method: Optional[str] = Field(None, description="Kullanılan yöntem (Tesseract veya EasyOCR)")
    text: Optional[str] = Field(None, description="Çıkarılan metin")
    total_characters: Optional[int] = Field(None, description="Toplam karakter sayısı")
    error: Optional[str] = Field(None, description="Hata mesajı (varsa)")

"""
Pydantic Semalari
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class PageData(BaseModel):
    page_number: int = Field(..., description="Sayfa numarasi")
    content: str = Field(..., description="Sayfa icerigi")


class FileInfo(BaseModel):
    filename: str = Field(..., description="Dosya adi")
    size_bytes: int = Field(..., description="Dosya boyutu (byte)")
    total_pages: int = Field(..., description="Toplam sayfa sayisi")


class PDFProcessResponse(BaseModel):
    success: bool
    message: str
    file_info: Optional[FileInfo] = None
    method: Optional[str] = None
    pages: Optional[List[PageData]] = None
    total_characters: Optional[int] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    ocr_ready: bool
    version: str


class ImageOCRResponse(BaseModel):
    success: bool
    message: str
    file_info: Optional[dict] = None
    method: Optional[str] = None
    text: Optional[str] = None
    total_characters: Optional[int] = None
    error: Optional[str] = None

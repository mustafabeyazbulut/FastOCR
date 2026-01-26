"""
PDF İşleme Servisi
PyMuPDF ve EasyOCR ile PDF'lerden metin çıkarma
"""

import fitz  # PyMuPDF
import easyocr
import pytesseract
import numpy as np
from PIL import Image
import os
import io
import platform
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Tesseract binary path ayarı
# Öncelik: 1) Env variable, 2) PATH, 3) Windows default path
tesseract_cmd = os.getenv('TESSERACT_CMD')
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    logger.info(f"✅ Tesseract env variable kullanılıyor: {tesseract_cmd}")
elif platform.system() == 'Windows':
    # Windows'ta PATH'te yoksa standart konumu dene
    default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(default_path):
        pytesseract.pytesseract.tesseract_cmd = default_path
        logger.info(f"✅ Tesseract default path'te bulundu: {default_path}")
    else:
        logger.info("ℹ️ Tesseract PATH'te aranacak (varsayılan)")
else:
    # Linux/Docker - PATH'te olmalı
    logger.info("ℹ️ Tesseract PATH'te aranacak (Linux/Docker)")


class PDFService:
    """PDF işleme servisi"""
    
    def __init__(self, languages: List[str] = ['tr', 'en']):
        """
        Args:
            languages: OCR için kullanılacak diller (tr=Türkçe, en=İngilizce)
        """
        self.languages = languages
        self._ocr_reader = None
        logger.info(f"🔧 PDFService oluşturuluyor - Diller: {languages}")
    
    def _ensure_ocr_ready(self):
        """OCR reader'ın yüklendiğinden emin ol"""
        if self._ocr_reader is None:
            logger.info(f"🔧 EasyOCR modeli yükleniyor...")
            logger.info(f"   📦 Seçilen diller: {self.languages}")
            logger.info(f"   🌐 Türkçe desteği: {'tr' in self.languages}")
            try:
                self._ocr_reader = easyocr.Reader(
                    self.languages, 
                    gpu=False,
                    verbose=False  # EasyOCR'ın kendi loglarını kapat
                )
                logger.info(f"✅ EasyOCR modeli başarıyla yüklendi - Diller: {self.languages}")
            except Exception as e:
                logger.error(f"❌ EasyOCR yükleme hatası: {e}")
                raise
    
    @property
    def is_ready(self) -> bool:
        """OCR motoru hazır mı?"""
        return True  # Her zaman hazır, gerektiğinde lazy-load yapar
    
    def extract_text_pymupdf(self, pdf_path: str) -> Dict:
        """
        PyMuPDF kullanarak PDF'den metin çıkarır.
        Metin tabanlı PDF'ler için en hızlı yöntem.
        
        Returns:
            dict: Sayfa numarası -> metin içeriği
        """
        result = {
            "method": "PyMuPDF",
            "pages": {},
            "total_pages": 0,
            "total_characters": 0
        }
        
        try:
            doc = fitz.open(pdf_path)
            result["total_pages"] = len(doc)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                result["pages"][page_num + 1] = text
                result["total_characters"] += len(text)
            
            doc.close()
            logger.info(f"✅ PyMuPDF ile {result['total_characters']} karakter çıkarıldı")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ PyMuPDF hatası: {e}")
        
        return result
    
    def extract_text_ocr(self, pdf_path: str) -> Dict:
        """
        EasyOCR kullanarak PDF'den metin çıkarır.
        Taranmış/görüntü PDF'ler için kullanılır.
        
        Args:
            pdf_path: PDF dosya yolu
        
        Returns:
            dict: Sayfa numarası -> metin içeriği
        """
        # OCR reader'ı lazy-load yap
        self._ensure_ocr_ready()
        
        result = {
            "method": "EasyOCR",
            "pages": {},
            "total_pages": 0,
            "total_characters": 0
        }
        
        try:
            doc = fitz.open(pdf_path)
            result["total_pages"] = len(doc)
            
            for page_num in range(len(doc)):
                logger.info(f"   ↳ Sayfa {page_num + 1}/{len(doc)} OCR işleniyor...")
                page = doc[page_num]
                
                # Yüksek çözünürlük için zoom matrisi (4x = 288 DPI)
                zoom = 4
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Pixmap'i PIL Image'a çevir
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Görüntü ön işleme - OCR kalitesini artır
                from PIL import ImageEnhance
                
                # Kontrast artır (1.5x)
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.5)
                
                # Keskinlik artır (2.0x)
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(2.0)
                
                # PIL Image'ı numpy array'e çevir
                image_np = np.array(image)
                
                # OCR uygula
                text_list = self._ocr_reader.readtext(image_np, detail=0, paragraph=True)
                text = "\n".join(text_list)
                
                result["pages"][page_num + 1] = text
                result["total_characters"] += len(text)
            
            doc.close()
            logger.info(f"✅ EasyOCR ile {result['total_characters']} karakter çıkarıldı")
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ EasyOCR hatası: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    def extract_text_tesseract(self, pdf_path: str, language: str = 'tur+eng') -> Dict:
        """
        Tesseract OCR kullanarak PDF'den metin çıkarır.
        Alfanumerik karakterler için genelde daha iyi sonuç verir.
        
        Args:
            pdf_path: PDF dosya yolu
            language: Tesseract dil kodu (tur=Türkçe, eng=İngilizce, tur+eng=Her ikisi)
        
        Returns:
            dict: Sayfa numarası -> metin içeriği
        """
        result = {
            "method": "Tesseract-OCR",
            "pages": {},
            "total_pages": 0,
            "total_characters": 0
        }
        
        try:
            doc = fitz.open(pdf_path)
            result["total_pages"] = len(doc)
            
            for page_num in range(len(doc)):
                logger.info(f"   ↳ Sayfa {page_num + 1}/{len(doc)} Tesseract OCR işleniyor...")
                page = doc[page_num]
                
                # Yüksek çözünürlük (4x = 288 DPI) - dengeli
                zoom = 4
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Pixmap'i PIL Image'a çevir
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Minimal görüntü işleme - en doğal sonuç
                from PIL import ImageEnhance
                
                # Hafif keskinlik - sadece bulanık kenarları düzelt
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.5)
                
                # Tesseract OCR uygula
                # PSM 6: Uniform text block (form/tablo için en iyi)
                # OEM 3: LSTM engine
                custom_config = r'--oem 3 --psm 6'
                
                text = pytesseract.image_to_string(
                    image, 
                    lang=language,
                    config=custom_config
                )
                
                result["pages"][page_num + 1] = text.strip()
                result["total_characters"] += len(text)
            
            doc.close()
            logger.info(f"✅ Tesseract ile {result['total_characters']} karakter çıkarıldı")
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Tesseract hatası: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    async def process_image(self, file_path: str, language: str = 'tur+eng') -> Dict:
        """
        Görüntü dosyasını OCR ile işler
        
        Args:
            file_path: Görüntü dosya yolu
            language: OCR dili (tur+eng, tur, eng)
            
        Returns:
            dict: İşlenmiş veri
        """
        try:
            result = {
                "method": "Tesseract-OCR",
                "text": "",
                "total_characters": 0
            }
            
            # Görüntüyü yükle
            image = Image.open(file_path)
            logger.info(f"📷 Görüntü yüklendi: {os.path.basename(file_path)}")
            
            # Minimal görüntü işleme
            from PIL import ImageEnhance
            
            # Hafif keskinlik
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.5)
            
            # Tesseract ile OCR
            try:
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(
                    image,
                    lang=language,
                    config=custom_config
                )
                result["text"] = text.strip()
                result["total_characters"] = len(text)
                result["method"] = "Tesseract-OCR"
                logger.info(f"✅ Tesseract ile {result['total_characters']} karakter çıkarıldı")
            except Exception as e:
                logger.warning(f"⚠️ Tesseract başarısız, EasyOCR deneniyor: {e}")
                # EasyOCR fallback
                self._ensure_ocr_ready()
                import numpy as np
                image_np = np.array(image)
                text_list = self._ocr_reader.readtext(image_np, detail=0, paragraph=True)
                text = "\n".join(text_list)
                result["text"] = text
                result["total_characters"] = len(text)
                result["method"] = "EasyOCR"
                logger.info(f"✅ EasyOCR ile {result['total_characters']} karakter çıkarıldı")
            
            # Dosya bilgilerini ekle
            result["file_info"] = {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size_bytes": os.path.getsize(file_path)
            }
            
            return result
        except Exception as e:
            logger.error(f"❌ Görüntü işleme hatası: {e}")
            raise
    
    def smart_extract(self, pdf_path: str, ocr_threshold: int = 100) -> Dict:
        """
        Akıllı çıkarma: Önce PyMuPDF dener, yeterli metin yoksa OCR kullanır.
        
        Args:
            pdf_path: PDF dosya yolu
            ocr_threshold: Bu karakterden az metin varsa OCR kullanılır
        
        Returns:
            dict: Çıkarılan veriler
        """
        # Önce PyMuPDF ile dene
        result = self.extract_text_pymupdf(pdf_path)
        
        # Yeterli metin var mı kontrol et
        if result.get("total_characters", 0) < ocr_threshold:
            logger.warning(f"⚠️ Metin az ({result.get('total_characters', 0)} karakter), OCR deneniyor...")
            # Önce Tesseract dene (daha iyi alfanumerik tanıma)
            try:
                result = self.extract_text_tesseract(pdf_path)
            except Exception as e:
                logger.warning(f"⚠️ Tesseract başarısız, EasyOCR'a geçiliyor: {e}")
                result = self.extract_text_ocr(pdf_path)
        
        # Dosya bilgilerini ekle
        result["file_info"] = {
            "path": pdf_path,
            "filename": os.path.basename(pdf_path),
            "size_bytes": os.path.getsize(pdf_path)
        }
        
        return result
    
    async def process_pdf(self, file_path: str) -> Dict:
        """
        PDF dosyasını işler (async wrapper)
        
        Args:
            file_path: PDF dosya yolu
            
        Returns:
            dict: İşlenmiş veri
        """
        try:
            # OCR işlemi CPU-intensive, ama basit upload için async wrapper yeterli
            # Gelecekte thread pool'a taşınabilir
            result = self.smart_extract(file_path)
            return result
        except Exception as e:
            logger.error(f"❌ PDF işleme hatası: {e}")
            raise


# Default instance (opsiyonel)
default_pdf_service = PDFService(['tr', 'en'])

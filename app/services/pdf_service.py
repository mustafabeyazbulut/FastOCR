import os
import warnings
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
warnings.filterwarnings('ignore', category=UserWarning)

import fitz  # PyMuPDF
import cv2
import numpy as np
import easyocr
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PDFService:
    """PDF isleme servisi - EasyOCR tabanli"""

    def __init__(self, languages: List[str] = ['tr', 'en']):
        self.languages = languages
        self._ocr_reader = None

    @property
    def is_ready(self) -> bool:
        return True

    def _ensure_ocr_ready(self):
        """EasyOCR modelini yukle"""
        if self._ocr_reader is None:
            use_gpu = os.getenv('USE_GPU', 'false').lower() == 'true'
            self._ocr_reader = easyocr.Reader(
                ['tr', 'en'],
                gpu=use_gpu,
                verbose=False
            )

    def preprocess_image(self, image_np):
        """Goruntu onisleme - kontrast artirma"""
        if len(image_np.shape) == 3 and image_np.shape[2] >= 3:
            lab = cv2.cvtColor(image_np, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return enhanced
        return image_np

    async def process_image(self, file_path: str, language: str = 'tr') -> Dict:
        """Goruntu dosyasini EasyOCR ile isle"""
        self._ensure_ocr_ready()

        result = {
            "method": "EasyOCR",
            "text": "",
            "total_characters": 0,
            "file_info": {
                "filename": os.path.basename(file_path),
                "size_bytes": os.path.getsize(file_path)
            }
        }

        try:
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError("Goruntu okunamadi.")

            print("  Goruntu isleniyor...", flush=True)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = self.preprocess_image(img)

            ocr_result = self._ocr_reader.readtext(img)

            lines = [text for (_, text, conf) in ocr_result if conf > 0.3]
            full_text = "\n".join(lines)

            result["text"] = full_text
            result["total_characters"] = len(full_text)
            return result
        except Exception as e:
            logger.error(f"Image OCR hatasi: {e}")
            result["error"] = str(e)
            return result

    def extract_text_ocr(self, pdf_path: str) -> Dict:
        """EasyOCR ile PDF'den metin cikar"""
        self._ensure_ocr_ready()

        result = {
            "method": "EasyOCR",
            "pages": {},
            "total_pages": 0,
            "total_characters": 0,
            "file_info": {
                "filename": os.path.basename(pdf_path),
                "size_bytes": os.path.getsize(pdf_path)
            }
        }

        try:
            doc = fitz.open(pdf_path)
            result["total_pages"] = len(doc)
            result["file_info"]["total_pages"] = len(doc)

            for page_num in range(len(doc)):
                print(f"  Sayfa {page_num + 1}/{len(doc)} isleniyor...", flush=True)
                page = doc[page_num]

                # Yuksek cozunurluk
                zoom = 3.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                img_data = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
                if pix.n == 4:
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_RGBA2RGB)
                elif pix.n == 1:
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_GRAY2RGB)

                img_data = self.preprocess_image(img_data)

                ocr_result = self._ocr_reader.readtext(img_data)

                lines = [text for (_, text, conf) in ocr_result if conf > 0.3]
                page_text = "\n".join(lines)

                result["pages"][page_num + 1] = page_text
                result["total_characters"] += len(page_text)

            doc.close()
            return result
        except Exception as e:
            logger.error(f"OCR hatasi: {e}")
            result["error"] = str(e)
            return result

    def smart_extract(self, pdf_path: str, ocr_threshold: int = 100) -> Dict:
        """Akilli cikarma: Dijital PDF ise hizli, taranmis ise OCR"""
        file_info = {
            "filename": os.path.basename(pdf_path),
            "size_bytes": os.path.getsize(pdf_path),
            "total_pages": 0
        }

        result = {
            "method": "Hybrid",
            "pages": {},
            "total_pages": 0,
            "total_characters": 0,
            "file_info": file_info
        }

        try:
            doc = fitz.open(pdf_path)
            total_chars = 0
            for page in doc:
                total_chars += len(page.get_text())
            file_info["total_pages"] = len(doc)
            doc.close()

            if total_chars > ocr_threshold:
                # Dijital PDF
                doc = fitz.open(pdf_path)
                result["method"] = "PyMuPDF (Digital)"
                result["total_pages"] = len(doc)
                for i, page in enumerate(doc):
                    text = page.get_text()
                    result["pages"][i+1] = text
                    result["total_characters"] += len(text)
                doc.close()
            else:
                # Taranmis PDF - EasyOCR
                ocr_result = self.extract_text_ocr(pdf_path)
                ocr_result["file_info"] = file_info
                return ocr_result

        except Exception as e:
            logger.error(f"SmartExtract hatasi: {e}")
            result["error"] = str(e)

        return result

    async def process_pdf(self, file_path: str) -> Dict:
        return self.smart_extract(file_path)


default_pdf_service = PDFService(['tr', 'en'])

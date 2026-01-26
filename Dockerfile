# Python 3.11 slim image kullan
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    # OpenCV ve görüntü işleme için
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # Tesseract OCR
    tesseract-ocr \
    tesseract-ocr-tur \
    tesseract-ocr-eng \
    # Wget (model indirme için)
    wget \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# ÖNEMLİ: EasyOCR modellerini ÖN-YÜKLE
# Bu sayede container çalışırken internete ihtiyaç duymaz
RUN python -c "import easyocr; reader = easyocr.Reader(['tr', 'en'], gpu=False, download_enabled=True); print('EasyOCR modelleri başarıyla yüklendi!')"

# Upload klasörünü oluştur
RUN mkdir -p /app/uploads

# Port 8000'i aç
EXPOSE 8000

# Healthcheck ekle
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Uygulamayı başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

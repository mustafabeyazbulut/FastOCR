# Python 3.11 slim image kullan
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-tur \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# EasyOCR modellerini ön-yükle (opsiyonel, ilk kullanımda otomatik indirir)
# RUN python -c "import easyocr; easyocr.Reader(['tr', 'en'])"

# Upload klasörünü oluştur
RUN mkdir -p /app/uploads

# Port 8000'i aç
EXPOSE 8000

# Uygulamayı başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

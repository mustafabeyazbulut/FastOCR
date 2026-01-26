# 🚀 FastOCR

**FastAPI tabanlı profesyonel OCR API servisi** - PDF ve görüntü dosyalarından metin çıkarma

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Özellikler

- 📄 **PDF Desteği**: Hem metin tabanlı hem taranmış PDF'ler
- 📷 **Görüntü Desteği**: JPG, PNG, JPEG, BMP, TIFF formatları
- 🔍 **Çift OCR Motoru**: 
  - **Tesseract OCR** (alfanumerik veriler için ideal)
  - **EasyOCR** (el yazısı ve karmaşık metinler için)
- 🌐 **Çoklu Dil**: Türkçe ve İngilizce tam desteği
- ⚡ **Hızlı**: AsyncIO destekli FastAPI
- 🐳 **Docker Ready**: Tek komutla deploy
- 📊 **Sayfa Numaralı Çıktı**: Her sayfa ayrı ayrı numaralandırılmış
- 🔐 **Güvenli**: UUID ile dosya çakışması önleme
- 📚 **Otomatik Dokümantasyon**: Swagger UI built-in

## 🎯 Kullanım Senaryoları

- ✅ Fatura/Evrak dijitalizasyonu
- ✅ Kimlik kartı/Pasaport okuma
- ✅ Şasi numarası/Plaka tanıma
- ✅ Form ve anket değerlendirme
- ✅ Otomatik belge arşivleme
- ✅ E-devlet entegrasyonları

## 📋 Gereksinimler

- Python 3.8+
- Tesseract OCR (sistem kurulumu)
- Docker (opsiyonel)

## 🚀 Hızlı Başlangıç

### Yöntem 1: Docker ile (Önerilen)

```bash
# Repository'yi klonla
git clone https://github.com/yourusername/FastOCR.git
cd FastOCR

# Tek komutla başlat
docker-compose up -d

# API hazır!
# http://localhost:8000/docs
```

### Yöntem 2: Lokal Kurulum

#### 1. Tesseract OCR Kurulumu

Tesseract, görüntülerden metin çıkaran açık kaynaklı bir OCR motorudur. Bu proje için **zorunludur**.

##### 🪟 Windows Kurulumu

**Seçenek A: Chocolatey ile (Önerilen)**
```bash
# Chocolatey yoksa önce kurun: https://chocolatey.org/install
# PowerShell'i YÖNETİCİ olarak açın ve:

choco install tesseract -y

# Kurulum sonrası doğrulama:
tesseract --version
```

**Seçenek B: Manuel Kurulum**
1. İndirin: https://github.com/UB-Mannheim/tesseract/wiki
2. **tesseract-ocr-w64-setup-5.x.x.exe** dosyasını indirin (en son versiyon)
3. Kurulum sırasında:
   - ✅ **"Additional language data"** kısmından **Turkish** seçin
   - ✅ **"Add to PATH"** seçeneğini işaretleyin
4. Kurulum sonrası **PowerShell'i yeniden başlatın**
5. Doğrulama:
   ```bash
   tesseract --version
   # Çıktı: tesseract 5.x.x
   ```

**PATH'e Manuel Ekleme (gerekirse):**
```bash
# Windows ortam değişkenlerine ekleyin:
# 1. Windows Arama → "Environment Variables"
# 2. "Path" → Edit → New
# 3. Ekleyin: C:\Program Files\Tesseract-OCR
# 4. PowerShell'i yeniden başlatın
```

##### 🐧 Linux Kurulumu (Ubuntu/Debian)

```bash
# Paket listesini güncelleyin
sudo apt-get update

# Tesseract ve dil paketlerini kurun
sudo apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-tur \
  tesseract-ocr-eng

# Doğrulama
tesseract --version
tesseract --list-langs
# Çıktı: eng, tur, osd
```

##### 🍎 macOS Kurulumu

```bash
# Homebrew ile kurun
brew install tesseract tesseract-lang

# Doğrulama
tesseract --version
tesseract --list-langs
```

##### ✅ Tesseract Kurulum Doğrulaması

Aşağıdaki komutları çalıştırarak kurulumu doğrulayın:

```bash
# Versiyon kontrolü
tesseract --version

# Dil paketlerini kontrol edin
tesseract --list-langs

# Türkçe ve İngilizce olmalı:
# List of available languages (3):
# eng
# osd
# tur
```

**Sorun mu var?**
- Windows'ta PATH'e eklenmediyse → Manuel PATH ekleme yap
- Linux'ta dil paketleri yoksa → `sudo apt-get install tesseract-ocr-tur tesseract-ocr-eng`
- macOS'ta dil paketleri yoksa → `brew install tesseract-lang`

#### 2. Python Bağımlılıklarını Yükle

```bash
# Virtual environment oluştur
python -m venv .venv

# Aktif et (Windows)
.venv\Scripts\activate
# Aktif et (Linux/Mac)
source .venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

#### 3. Servisi Başlat

```bash
uvicorn app.main:app --reload

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📖 API Kullanımı

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "ocr_ready": true,
  "version": "1.0.0"
}
```

### 2. PDF İşleme

```bash
curl -X POST "http://localhost:8000/api/v1/upload-pdf" \
  -F "file=@document.pdf" \
  -F "language=tr,en"
```

**Response:**
```json
{
  "success": true,
  "message": "PDF başarıyla işlendi! 5 sayfa, 2450 karakter.",
  "file_info": {
    "filename": "document.pdf",
    "size_bytes": 236350,
    "total_pages": 5
  },
  "method": "Tesseract-OCR",
  "pages": [
    {
      "page_number": 1,
      "content": "1. Sayfa:\nSayfa içeriği..."
    }
  ],
  "total_characters": 2450
}
```

### 3. Görüntü İşleme

```bash
curl -X POST "http://localhost:8000/api/v1/upload-image" \
  -F "file=@photo.jpg" \
  -F "language=tur+eng"
```

**Response:**
```json
{
  "success": true,
  "message": "Görüntü başarıyla işlendi! 1234 karakter.",
  "method": "Tesseract-OCR",
  "text": "Çıkarılan metin...",
  "total_characters": 1234
}
```

### Dil Seçenekleri

- `tr` veya `tur`: Sadece Türkçe
- `en` veya `eng`: Sadece İngilizce  
- `tr,en` veya `tur+eng`: Her ikisi (varsayılan)

## 🐍 Python Örneği

```python
import requests

# PDF yükle
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/upload-pdf",
        files={"file": f},
        data={"language": "tr,en"}
    )
    
    result = response.json()
    if result["success"]:
        for page in result["pages"]:
            print(f"Sayfa {page['page_number']}:")
            print(page["content"][:200])
```

## 📁 Proje Yapısı

```
FastOCR/
├── app/
│   ├── main.py              # FastAPI uygulaması
│   ├── api/
│   │   └── endpoints.py     # API endpoints
│   ├── services/
│   │   └── pdf_service.py   # OCR servisi
│   └── models/
│       └── schemas.py       # Pydantic modelleri
├── tests/
│   └── test_api.py          # API testleri
├── Dockerfile               # Docker image
├── docker-compose.yaml      # Docker Compose
├── requirements.txt         # Python bağımlılıkları
└── README.md
```

## 🔧 Yapılandırma

### Port Değiştirme

**docker-compose.yaml:**
```yaml
ports:
  - "9000:8000"  # Port 9000'e değiştir
```

**Lokal:**
```bash
uvicorn app.main:app --port 9000
```

### Tesseract Path (Windows)

Eğer Tesseract PATH'te değilse:
```bash
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
uvicorn app.main:app
```

## 🧪 Testler

```bash
# Tüm testleri çalıştır
pytest tests/ -v

# Kod coverage
pytest tests/ --cov=app
```

## 🐳 Docker Komutları

```bash
# Build ve başlat
docker-compose up --build

# Arka planda çalıştır
docker-compose up -d

# Logları görüntüle
docker-compose logs -f

# Durdur
docker-compose down

# Yeniden başlat
docker-compose restart
```

## 🌐 Production Deployment

### Docker ile Deploy

```bash
# Production build
docker-compose -f docker-compose.prod.yaml up -d

# Nginx reverse proxy ile kullanım önerilir
```

### Güvenlik Önerileri

- ✅ CORS ayarlarını spesifik domainler ile sınırla
- ✅ Rate limiting ekle
- ✅ API key authentication ekle
- ✅ HTTPS kullan
- ✅ Dosya boyutu limitleri koy

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR motoru
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Deep learning OCR
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF işleme

## 📧 İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

**Geliştirici:** FastOCR Team  
**Versiyon:** 1.0.0  
**Son Güncelleme:** 2026-01-26

⭐ Beğendiyseniz yıldız vermeyi unutmayın!

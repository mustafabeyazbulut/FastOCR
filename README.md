# FastOCR

PDF ve goruntu dosyalarindan metin cikarma API servisi.

## Ozellikler

- **PDF Destegi**: Dijital ve taranmis PDF'ler
- **Goruntu Destegi**: JPG, PNG, BMP, TIFF
- **Turkce Destegi**: EasyOCR ile tam Turkce karakter destegi (s, g, u, o, i, c)
- **Otomatik Algilama**: Dijital PDF'ler hizli, taranmis PDF'ler OCR ile islenir
- **Docker Ready**: Tek komutla deploy

## Hizli Baslangic

### Docker ile (Onerilen)

```bash
git clone https://github.com/yourusername/FastOCR.git
cd FastOCR
docker-compose up -d
```

API: http://localhost:8000/docs

### Lokal Kurulum

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Kullanimi

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

### PDF Isleme

```bash
curl -X POST "http://localhost:8000/api/v1/upload-pdf" \
  -F "file=@document.pdf"
```

### Goruntu Isleme

```bash
curl -X POST "http://localhost:8000/api/v1/upload-image" \
  -F "file=@photo.jpg"
```

## Python Ornegi

```python
import requests

with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/upload-pdf",
        files={"file": f}
    )
    result = response.json()
    for page in result["pages"]:
        print(page["content"])
```

## Proje Yapisi

```
FastOCR/
├── app/
│   ├── main.py           # FastAPI uygulamasi
│   ├── api/
│   │   └── endpoints.py  # API endpoints
│   ├── services/
│   │   └── pdf_service.py # EasyOCR servisi
│   └── models/
│       └── schemas.py    # Pydantic modelleri
├── Dockerfile
├── docker-compose.yaml
└── requirements.txt
```

## Docker Komutlari

```bash
docker-compose up --build    # Build ve baslat
docker-compose up -d         # Arka planda
docker-compose logs -f       # Loglar
docker-compose down          # Durdur
```

## Teknik Detaylar

- **OCR Motoru**: EasyOCR (Turkce + Ingilizce)
- **PDF Okuma**: PyMuPDF
- **Framework**: FastAPI
- **Goruntu Isleme**: OpenCV

## Lisans

MIT

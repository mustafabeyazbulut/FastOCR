"""
API Test Senaryoları
FastAPI uygulaması için pytest testleri
"""

import pytest
from httpx import AsyncClient
from app.main import app
import os
from pathlib import Path


@pytest.mark.asyncio
async def test_health_check():
    """Health check endpoint testi"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ocr_ready" in data
        assert "version" in data
        print("✅ Health check testi başarılı")


@pytest.mark.asyncio
async def test_root_endpoint():
    """Ana sayfa endpoint testi"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        print("✅ Ana sayfa testi başarılı")


@pytest.mark.asyncio
async def test_upload_pdf_not_pdf_file():
    """Yanlış dosya formatı testi"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Fake bir txt dosyası gönder
        files = {"file": ("test.txt", b"fake content", "text/plain")}
        data = {"language": "tr"}
        
        response = await client.post("/api/v1/upload-pdf", files=files, data=data)
        
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]
        print("✅ Yanlış format testi başarılı")


@pytest.mark.asyncio
async def test_upload_pdf_with_real_file():
    """
    Gerçek PDF dosyası ile test
    Not: Bu test için proje klasöründe bir PDF olması gerekir
    """
    # Test klasöründeki PDF'leri bul
    pdf_files = list(Path("tests").glob("*.pdf"))
    if not pdf_files:
        # Üst klasörde de dene
        pdf_files = list(Path(".").glob("*.pdf"))
    
    if not pdf_files:
        pytest.skip("Test için PDF dosyası bulunamadı")
        return
    
    test_pdf = pdf_files[0]
    
    async with AsyncClient(app=app, base_url="http://test", timeout=120.0) as client:
        with open(test_pdf, "rb") as f:
            files = {"file": (test_pdf.name, f, "application/pdf")}
            data = {"language": "tr,en"}
            
            response = await client.post("/api/v1/upload-pdf", files=files, data=data)
            
            # Response kontrolü
            assert response.status_code == 200
            result = response.json()
            
            assert result["success"] is True
            assert result["message"] is not None
            assert result["file_info"] is not None
            assert result["pages"] is not None
            assert result["total_characters"] > 0
            
            # Sayfa verilerini kontrol et
            pages = result["pages"]
            assert len(pages) > 0
            
            # İlk sayfa formatını kontrol et
            first_page = pages[0]
            assert "page_number" in first_page
            assert "content" in first_page
            assert "1. Sayfa:" in first_page["content"]
            
            print(f"\n✅ PDF Upload Testi Başarılı!")
            print(f"   📄 Dosya: {test_pdf.name}")
            print(f"   📊 Sayfa Sayısı: {result['file_info']['total_pages']}")
            print(f"   🔤 Toplam Karakter: {result['total_characters']}")
            print(f"   🛠️ Yöntem: {result['method']}")
            print(f"\n   📝 İlk 200 karakter:")
            print(f"   {pages[0]['content'][:200]}...")


@pytest.mark.asyncio
async def test_language_options():
    """Farklı dil seçenekleri testi"""
    pdf_files = list(Path("tests").glob("*.pdf"))
    if not pdf_files:
        pdf_files = list(Path(".").glob("*.pdf"))
    
    if not pdf_files:
        pytest.skip("Test için PDF dosyası bulunamadı")
        return
    
    test_pdf = pdf_files[0]
    
    languages_to_test = ["tr", "en", "tr,en"]
    
    for lang in languages_to_test:
        async with AsyncClient(app=app, base_url="http://test", timeout=120.0) as client:
            with open(test_pdf, "rb") as f:
                files = {"file": (test_pdf.name, f, "application/pdf")}
                data = {"language": lang}
                
                response = await client.post("/api/v1/upload-pdf", files=files, data=data)
                
                assert response.status_code == 200
                result = response.json()
                assert result["success"] is True
                
                print(f"✅ Dil testi başarılı: {lang}")


def test_project_structure():
    """Proje yapısı kontrolü"""
    required_dirs = ["app", "app/api", "app/services", "app/models", "tests", "uploads"]
    required_files = [
        "app/__init__.py",
        "app/main.py",
        "app/api/endpoints.py",
        "app/services/pdf_service.py",
        "app/models/schemas.py",
        "requirements.txt",
        "Dockerfile",
        "docker-compose.yaml"
    ]
    
    for directory in required_dirs:
        assert Path(directory).exists(), f"Klasör eksik: {directory}"
    
    for file in required_files:
        assert Path(file).exists(), f"Dosya eksik: {file}"
    
    print("✅ Proje yapısı kontrolü başarılı")


if __name__ == "__main__":
    print("🧪 Test Senaryoları Başlatılıyor...")
    print("=" * 60)
    pytest.main([__file__, "-v", "-s"])

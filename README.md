# YouTube Video Dönüştürücü

YouTube videolarını MP3 veya MP4 formatında indirmenizi sağlayan modern web uygulaması.

## 🚀 Özellikler

- ✅ YouTube videolarını MP3 (ses) formatında indirme
- ✅ YouTube videolarını MP4 (video) formatında indirme
- ✅ Farklı kalite seçenekleri (128kbps-320kbps, 360p-1080p)
- ✅ Modern ve responsive kullanıcı arayüzü
- ✅ Gerçek zamanlı indirme durumu takibi
- ✅ Otomatik dosya indirme
- ✅ Docker desteği
- ✅ Production-ready yapılandırma
- ✅ Nginx reverse proxy
- ✅ Health check endpoint'leri
- ✅ Rate limiting ve güvenlik

## 📋 Gereksinimler

- Python 3.11+
- Docker & Docker Compose (önerilen)
- RapidAPI ve Apify API anahtarları

## 🐳 Docker ile Kurulum (Önerilen)

### 1. Projeyi Klonlayın
```bash
git clone <repository-url>
cd youtube-converter
```

### 2. Environment Variables Ayarlayın
```bash
cp .env.example .env
```

`.env` dosyasını düzenleyerek API anahtarlarınızı girin:
```env
RAPIDAPI_KEY=your-rapidapi-key-here
APPIFY_TOKEN=your-apify-token-here
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key
```

### 3. Docker Compose ile Başlatın
```bash
docker-compose up -d
```

### 4. Uygulamaya Erişin
- Web Arayüzü: http://localhost
- API: http://localhost/api
- Health Check: http://localhost/api/health

## 🔧 Manuel Kurulum

### 1. Python Sanal Ortamı Oluşturun
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### 2. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 3. Environment Variables Ayarlayın
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

### 4. Uygulamayı Başlatın

**Development:**
```bash
python app.py
```

**Production:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
```

## 🔑 API Anahtarları

### RapidAPI YouTube Downloader
1. [RapidAPI](https://rapidapi.com) hesabı oluşturun
2. YouTube Media Downloader API'sine abone olun
3. API anahtarınızı kopyalayın

### Apify YouTube Downloader
1. [Apify](https://apify.com) hesabı oluşturun
2. API token'ınızı alın
3. YouTube Video Downloader actor'ünü kullanın

## Kullanım

1. **YouTube URL'sini Girin**: İndirmek istediğiniz videonun URL'sini yapıştırın
2. **Format Seçin**: MP4 (video) veya MP3 (sadece ses) formatını seçin
3. **Kalite Belirleyin**: İstediğiniz kalite seviyesini seçin
4. **İndirin**: "İndir" butonuna tıklayın ve işlemin tamamlanmasını bekleyin

## API Endpoints

### POST /api/download
İndirme işlemini başlatır.

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "format": "mp4", // veya "mp3"
    "quality": "720p" // veya "best", "1080p", "480p", "360p"
}
```

### GET /api/status/{task_id}
İndirme durumunu kontrol eder.

### GET /api/download-file/{task_id}
İndirilen dosyayı indirir.

### GET /api/health
API sağlık durumunu kontrol eder.

## Proje Yapısı

```
YT dönüştürücü/
├── app.py              # Flask backend servisi
├── index.html          # Ana web arayüzü
├── style.css           # CSS stilleri
├── script.js           # JavaScript fonksiyonları
├── requirements.txt    # Python bağımlılıkları
├── README.md          # Bu dosya
└── downloads/         # İndirilen dosyalar (otomatik oluşturulur)
```

## Güvenlik Notları

- Bu uygulama sadece kişisel kullanım içindir
- Telif hakkı kurallarına uygun kullanın
- İndirilen dosyalar 1 saat sonra otomatik olarak silinir
- Uygulama yerel ağınızda çalışır, internet üzerinden erişilemez

## Sorun Giderme

### "FFmpeg bulunamadı" Hatası
- FFmpeg'in doğru kurulduğundan ve PATH'e eklendiğinden emin olun
- Terminal/Command Prompt'ta `ffmpeg -version` komutunu test edin

### "Video mevcut değil" Hatası
- Video URL'sinin doğru olduğundan emin olun
- Video özel veya yaş kısıtlamalı olabilir
- Video kaldırılmış olabilir

### İndirme Çok Yavaş
- İnternet bağlantınızı kontrol edin
- Daha düşük kalite seçeneği deneyin
- Başka bir zamanda tekrar deneyin

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Kişisel kullanım için serbesttir.

## 🌐 GitHub Hosting

### Hızlı GitHub Deployment

1. **Repository Oluşturun**:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

2. **GitHub Secrets Ayarlayın**:
   - Repository Settings > Secrets and variables > Actions
   - Gerekli secrets'ları ekleyin:
     - `RAPIDAPI_KEY`: RapidAPI anahtarınız
     - `APPIFY_TOKEN`: Apify token'ınız
     - `HEROKU_API_KEY`: Heroku API anahtarı (opsiyonel)
     - `RAILWAY_TOKEN`: Railway token'ı (opsiyonel)

3. **GitHub Pages Aktifleştirin**:
   - Repository Settings > Pages
   - Source: "GitHub Actions" seçin

4. **Backend Deployment**:
   - **Heroku**: Ücretsiz tier mevcut
   - **Railway**: $5/ay'dan başlayan planlar
   - **Docker Hub**: Container registry için

### Deployment Seçenekleri

#### Option 1: GitHub Pages + Heroku
- **Frontend**: `https://USERNAME.github.io/REPO_NAME`
- **Backend**: `https://APP_NAME.herokuapp.com`
- **Maliyet**: Ücretsiz (Heroku free tier)

#### Option 2: GitHub Pages + Railway
- **Frontend**: `https://USERNAME.github.io/REPO_NAME`
- **Backend**: `https://PROJECT.up.railway.app`
- **Maliyet**: $5/ay (Railway)

### Otomatik CI/CD

GitHub Actions workflow'u otomatik olarak:
- ✅ Kodu test eder
- ✅ Docker image'ı build eder
- ✅ Frontend'i GitHub Pages'e deploy eder
- ✅ Backend'i seçilen servise deploy eder
- ✅ Deployment durumunu bildirir

### Detaylı Talimatlar

Kapsamlı GitHub hosting rehberi için `DEPLOYMENT.md` dosyasına bakın.

## Katkıda Bulunma

Hata raporları ve öneriler için GitHub Issues kullanabilirsiniz.

---

**Not**: Bu araç eğitim amaçlıdır. YouTube'un hizmet şartlarına ve telif hakkı yasalarına uygun kullanın.
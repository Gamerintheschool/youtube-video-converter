# GitHub Hosting ve Deployment Rehberi

Bu rehber, YouTube Video Dönüştürücü uygulamasını GitHub üzerinden nasıl host edeceğinizi açıklar.

## 🚀 Hızlı Başlangıç

### 1. Repository Oluşturma

1. GitHub'da yeni bir repository oluşturun
2. Bu projeyi repository'nize push edin:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git
git push -u origin main
```

### 2. GitHub Secrets Yapılandırması

Repository Settings > Secrets and variables > Actions bölümünden aşağıdaki secrets'ları ekleyin:

#### 🔑 Zorunlu Secrets

| Secret Adı | Açıklama | Örnek |
|------------|----------|-------|
| `RAPIDAPI_KEY` | RapidAPI YouTube Downloader API anahtarı | `abc123def456...` |
| `APPIFY_TOKEN` | Apify YouTube Scraper token'ı | `apify_api_xyz789...` |

#### 🐳 Docker Hub (Opsiyonel)

| Secret Adı | Açıklama |
|------------|----------|
| `DOCKER_USERNAME` | Docker Hub kullanıcı adı |
| `DOCKER_PASSWORD` | Docker Hub şifresi veya access token |

#### 🚀 Heroku Deployment (Opsiyonel)

| Secret Adı | Açıklama |
|------------|----------|
| `HEROKU_API_KEY` | Heroku API anahtarı |
| `HEROKU_APP_NAME` | Heroku uygulama adı |
| `HEROKU_EMAIL` | Heroku hesap email'i |

#### 🚄 Railway Deployment (Opsiyonel)

| Secret Adı | Açıklama |
|------------|----------|
| `RAILWAY_TOKEN` | Railway API token'ı |
| `RAILWAY_SERVICE_NAME` | Railway servis adı (varsayılan: youtube-converter) |

### 3. GitHub Pages Aktifleştirme

1. Repository Settings > Pages bölümüne gidin
2. Source olarak "GitHub Actions" seçin
3. İlk deployment otomatik olarak başlayacak

### 4. Variables Yapılandırması

Repository Settings > Secrets and variables > Actions > Variables sekmesinden:

| Variable Adı | Açıklama | Örnek |
|--------------|----------|-------|
| `BACKEND_URL` | Backend servis URL'i | `https://your-app.herokuapp.com` |

## 📋 Deployment Seçenekleri

### Option 1: GitHub Pages + Heroku

**Frontend**: GitHub Pages (Ücretsiz)
**Backend**: Heroku (Ücretsiz tier mevcut)

1. Heroku hesabı oluşturun
2. Heroku CLI yükleyin
3. GitHub secrets'ları yapılandırın
4. Push yapın - otomatik deployment başlar

**Erişim**:
- Frontend: `https://KULLANICI_ADI.github.io/REPO_ADI`
- Backend: `https://UYGULAMA_ADI.herokuapp.com`

### Option 2: GitHub Pages + Railway

**Frontend**: GitHub Pages (Ücretsiz)
**Backend**: Railway ($5/ay'dan başlayan planlar)

1. Railway hesabı oluşturun
2. GitHub ile bağlayın
3. API token'ı alın
4. GitHub secrets'ları yapılandırın

**Erişim**:
- Frontend: `https://KULLANICI_ADI.github.io/REPO_ADI`
- Backend: `https://PROJE_ADI.up.railway.app`

### Option 3: Sadece GitHub Pages (Sınırlı)

**Not**: Bu seçenek sadece frontend'i host eder. Backend için ayrı bir servis gerekir.

## 🔧 Yapılandırma Dosyaları

### GitHub Actions Workflow
- `.github/workflows/deploy.yml` - Ana deployment pipeline
- Otomatik test, build ve deployment
- Multi-platform support

### Backend Deployment
- `Procfile` - Heroku için
- `railway.json` - Railway için
- `app.json` - Heroku app manifest

### Frontend Yapılandırması
- `static/config.js` - API endpoint yapılandırması
- Otomatik backend URL detection

## 🛠️ Manuel Deployment

### Heroku CLI ile

```bash
# Heroku CLI yükleyin
npm install -g heroku

# Login olun
heroku login

# Uygulama oluşturun
heroku create your-app-name

# Environment variables ayarlayın
heroku config:set RAPIDAPI_KEY=your-key
heroku config:set APPIFY_TOKEN=your-token
heroku config:set FLASK_ENV=production

# Deploy edin
git push heroku main
```

### Railway CLI ile

```bash
# Railway CLI yükleyin
npm install -g @railway/cli

# Login olun
railway login

# Proje oluşturun
railway new

# Environment variables ayarlayın
railway variables set RAPIDAPI_KEY=your-key
railway variables set APPIFY_TOKEN=your-token

# Deploy edin
railway up
```

## 🔍 Monitoring ve Debugging

### GitHub Actions Logs
- Repository > Actions sekmesinden workflow loglarını görüntüleyin
- Her step'in detaylı çıktısını inceleyebilirsiniz

### Backend Logs

**Heroku**:
```bash
heroku logs --tail -a your-app-name
```

**Railway**:
```bash
railway logs
```

### Health Check
Backend servisinizin sağlığını kontrol edin:
```bash
curl https://your-backend-url.com/api/health
```

## 🚨 Troubleshooting

### Yaygın Sorunlar

**1. API Keys Çalışmıyor**
- GitHub secrets'ların doğru ayarlandığından emin olun
- Secret adlarının tam olarak eşleştiğinden emin olun

**2. CORS Hataları**
- Backend'de CORS_ORIGINS environment variable'ını ayarlayın
- Frontend domain'ini backend'e ekleyin

**3. Build Hataları**
- Requirements.txt'deki paket versiyonlarını kontrol edin
- Python versiyonunun uyumlu olduğundan emin olun

**4. Deployment Başarısız**
- GitHub Actions loglarını kontrol edin
- Secrets'ların doğru ayarlandığından emin olun
- Heroku/Railway hesap limitlerini kontrol edin

### Debug Komutları

```bash
# Local test
python app.py

# Docker test
docker build -t youtube-converter .
docker run -p 5000:5000 --env-file .env youtube-converter

# GitHub Actions local test (act tool ile)
act -j test
```

## 📞 Destek

Sorun yaşıyorsanız:
1. Bu dokümantasyonu tekrar okuyun
2. GitHub Issues'da sorun bildirin
3. Logs'ları kontrol edin ve hata mesajlarını paylaşın

## 🔄 Güncelleme

Uygulama güncellemeleri için:
1. Kodu güncelleyin
2. Git'e commit edin
3. Main branch'e push edin
4. GitHub Actions otomatik olarak yeni deployment yapacak

```bash
git add .
git commit -m "Update: new features"
git push origin main
```
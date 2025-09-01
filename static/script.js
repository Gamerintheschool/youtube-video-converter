class YouTubeConverter {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        // API URL'sini config'den al
        this.apiUrl = this.getApiUrl();
    }

    getApiUrl() {
        // Config.js'den backend URL'ini al
        if (typeof CONFIG !== 'undefined') {
            return CONFIG.BACKEND_URL + '/api';
        }
        
        // Fallback: Geliştirme ortamında localhost, production'da mevcut domain kullan
        const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        
        if (isDevelopment) {
            return 'http://localhost:5000/api';
        } else {
            // Production ortamında aynı domain'i kullan
            return `${window.location.protocol}//${window.location.host}/api`;
        }
    }

    initializeElements() {
        this.videoUrlInput = document.getElementById('videoUrl');
        this.pasteBtn = document.getElementById('pasteBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.qualitySelect = document.getElementById('qualitySelect');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.resultContainer = document.getElementById('resultContainer');
        this.errorContainer = document.getElementById('errorContainer');
        this.errorText = document.getElementById('errorText');
        this.downloadLink = document.getElementById('downloadLink');
    }

    bindEvents() {
        this.pasteBtn.addEventListener('click', () => this.pasteFromClipboard());
        this.downloadBtn.addEventListener('click', () => this.startDownload());
        
        // Format değişikliğinde kalite seçeneklerini güncelle
        document.querySelectorAll('input[name="format"]').forEach(radio => {
            radio.addEventListener('change', () => this.updateQualityOptions());
        });

        // URL input validation
        this.videoUrlInput.addEventListener('input', () => this.validateUrl());
    }

    async pasteFromClipboard() {
        try {
            const text = await navigator.clipboard.readText();
            if (this.isValidYouTubeUrl(text)) {
                this.videoUrlInput.value = text;
                this.validateUrl();
            } else {
                this.showError('Geçerli bir YouTube URL\'si bulunamadı!');
            }
        } catch (err) {
            console.error('Clipboard okuma hatası:', err);
            this.showError('Panoya erişim izni gerekli!');
        }
    }

    isValidYouTubeUrl(url) {
        const youtubeRegex = /^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        return youtubeRegex.test(url);
    }

    validateUrl() {
        const url = this.videoUrlInput.value.trim();
        const isValid = url && this.isValidYouTubeUrl(url);
        
        this.downloadBtn.disabled = !isValid;
        
        if (url && !isValid) {
            this.videoUrlInput.style.borderColor = '#dc3545';
        } else {
            this.videoUrlInput.style.borderColor = '#e1e5e9';
        }
        
        return isValid;
    }

    updateQualityOptions() {
        const selectedFormat = document.querySelector('input[name="format"]:checked').value;
        const qualitySelect = this.qualitySelect;
        
        // Mevcut seçenekleri temizle
        qualitySelect.innerHTML = '';
        
        if (selectedFormat === 'mp4') {
            const videoQualities = [
                { value: 'best', text: 'En İyi Kalite' },
                { value: '1080p', text: '1080p (Full HD)' },
                { value: '720p', text: '720p (HD)' },
                { value: '480p', text: '480p' },
                { value: '360p', text: '360p' }
            ];
            
            videoQualities.forEach(quality => {
                const option = document.createElement('option');
                option.value = quality.value;
                option.textContent = quality.text;
                qualitySelect.appendChild(option);
            });
        } else {
            const audioQualities = [
                { value: 'best', text: 'En İyi Kalite (320kbps)' },
                { value: '256', text: '256kbps' },
                { value: '192', text: '192kbps' },
                { value: '128', text: '128kbps' }
            ];
            
            audioQualities.forEach(quality => {
                const option = document.createElement('option');
                option.value = quality.value;
                option.textContent = quality.text;
                qualitySelect.appendChild(option);
            });
        }
    }

    async startDownload() {
        if (!this.validateUrl()) {
            this.showError('Lütfen geçerli bir YouTube URL\'si girin!');
            return;
        }

        const url = this.videoUrlInput.value.trim();
        const format = document.querySelector('input[name="format"]:checked').value;
        const quality = this.qualitySelect.value;

        this.showProgress();
        this.downloadBtn.disabled = true;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 saniye timeout

            const response = await fetch(`${this.apiUrl}/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: url,
                    format: format,
                    quality: quality
                }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}: İndirme başarısız!`);
            }

            const data = await response.json();
            
            if (data.success) {
                this.pollDownloadStatus(data.task_id);
            } else {
                throw new Error(data.error || 'İndirme başlatılamadı!');
            }

        } catch (error) {
            if (error.name === 'AbortError') {
                this.showError('İstek zaman aşımına uğradı. Lütfen tekrar deneyin.');
            } else {
                console.error('İndirme hatası:', error);
                this.showError(error.message || 'İndirme sırasında bir hata oluştu!');
            }
            this.hideProgress();
            this.downloadBtn.disabled = false;
        }
    }

    async pollDownloadStatus(taskId, retryCount = 0, startTime = null) {
        const maxRetries = 3;
        const maxPollTime = 10 * 60 * 1000; // 10 dakika maksimum bekleme
        if (!startTime) {
            startTime = Date.now();
        }

        try {
            // Maksimum bekleme süresini kontrol et
            if (Date.now() - startTime > maxPollTime) {
                throw new Error('İndirme işlemi çok uzun sürdü. Lütfen tekrar deneyin.');
            }

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 saniye timeout

            const response = await fetch(`${this.apiUrl}/status/${taskId}`, {
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Durum kontrolü başarısız!`);
            }

            const data = await response.json();

            if (data.status === 'completed') {
                this.showSuccess(data.download_url, data.filename);
                this.hideProgress();
                this.downloadBtn.disabled = false;
            } else if (data.status === 'failed') {
                throw new Error(data.error || 'İndirme başarısız!');
            } else {
                // Hala işleniyor
                this.updateProgress(data.progress || 0, data.message || 'İşleniyor...');
                setTimeout(() => this.pollDownloadStatus(taskId, 0, startTime), 3000); // 3 saniye bekle
            }
        } catch (error) {
            if (error.name === 'AbortError' && retryCount < maxRetries) {
                // Timeout durumunda tekrar dene
                console.warn(`Durum kontrolü timeout (${retryCount + 1}/${maxRetries})`);
                setTimeout(() => this.pollDownloadStatus(taskId, retryCount + 1, startTime), 5000);
                return;
            }
            
            console.error('Durum kontrolü hatası:', error);
            this.showError(error.message || 'Durum kontrolü başarısız!');
            this.hideProgress();
            this.downloadBtn.disabled = false;
        }
    }

    showProgress() {
        this.hideError();
        this.hideResult();
        this.progressContainer.style.display = 'block';
        this.updateProgress(0, 'İndirme başlatılıyor...');
    }

    updateProgress(percent, message) {
        this.progressBar.style.width = `${percent}%`;
        this.progressText.textContent = message;
    }

    hideProgress() {
        this.progressContainer.style.display = 'none';
    }

    showSuccess(downloadUrl, filename) {
        this.hideError();
        this.hideProgress();
        
        // İndirme linkini ayarla
        this.downloadLink.href = downloadUrl;
        this.downloadLink.download = filename;
        this.resultContainer.style.display = 'block';
        
        // Otomatik indirme başlat
        this.startAutomaticDownload(downloadUrl, filename);
    }
    
    async startAutomaticDownload(downloadUrl, filename) {
        try {
            // Dosya adını optimize et
            const optimizedFilename = this.optimizeFilename(filename);
            
            // Proxy endpoint üzerinden dosyayı al
            const response = await fetch(`${this.apiUrl}/proxy-download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    download_url: downloadUrl
                })
            });
            
            if (!response.ok) {
                throw new Error('Proxy indirme başarısız oldu');
            }
            
            // Blob olarak oku
            const blob = await response.blob();
            
            // İndirme linkini oluştur
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = optimizedFilename;
            
            // DOM'a ekle ve tıkla
            document.body.appendChild(a);
            a.click();
            
            // Temizle
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Başarı mesajı göster
            this.showDownloadNotification(`Dosya başarıyla indirildi: ${optimizedFilename}`, 'success');
            
        } catch (error) {
            console.error('Otomatik indirme hatası:', error);
            this.showDownloadNotification('Otomatik indirme başarısız. Manuel indirme linkini kullanın.', 'warning');
        }
    }
    
    optimizeFilename(filename) {
        if (!filename) return 'download';
        
        // Dosya uzantısını ayır
        const lastDotIndex = filename.lastIndexOf('.');
        const name = lastDotIndex > 0 ? filename.substring(0, lastDotIndex) : filename;
        const extension = lastDotIndex > 0 ? filename.substring(lastDotIndex) : '';
        
        // Geçersiz karakterleri temizle
        let cleanName = name
            .replace(/[<>:"/\\|?*]/g, '') // Windows geçersiz karakterleri
            .replace(/[\x00-\x1f\x80-\x9f]/g, '') // Kontrol karakterleri
            .replace(/^\.|\.$/, '') // Başta ve sonda nokta
            .replace(/\s+/g, ' ') // Çoklu boşlukları tek boşluğa çevir
            .trim(); // Başta ve sonda boşluk temizle
        
        // Çok uzun isimleri kısalt (Windows 255 karakter sınırı)
        if (cleanName.length > 200) {
            cleanName = cleanName.substring(0, 200) + '...';
        }
        
        // Boş isim kontrolü
        if (!cleanName) {
            cleanName = 'youtube_download';
        }
        
        return cleanName + extension;
    }
    
    showDownloadNotification(message, type = 'info') {
        // Bildirim elementi oluştur
        const notification = document.createElement('div');
        notification.className = `download-notification ${type}`;
        notification.textContent = message;
        
        // Stil ekle
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        
        // Tip'e göre renk ayarla
        if (type === 'success') {
            notification.style.backgroundColor = '#4CAF50';
        } else if (type === 'warning') {
            notification.style.backgroundColor = '#FF9800';
        } else {
            notification.style.backgroundColor = '#2196F3';
        }
        
        // DOM'a ekle
        document.body.appendChild(notification);
        
        // 4 saniye sonra kaldır
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    hideResult() {
        this.resultContainer.style.display = 'none';
    }

    showError(message) {
        this.hideProgress();
        this.hideResult();
        
        this.errorText.textContent = message;
        this.errorContainer.style.display = 'block';
        
        // 5 saniye sonra hata mesajını gizle
        setTimeout(() => this.hideError(), 5000);
    }

    hideError() {
        this.errorContainer.style.display = 'none';
    }
}

// Sayfa yüklendiğinde uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    new YouTubeConverter();
});

// Service Worker kaydı (offline çalışma için)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
from flask import Flask, request, jsonify, redirect, Response
from flask_cors import CORS
import requests
import os
import uuid
import threading
import time
from datetime import datetime
import json
import re
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Production CORS configuration
if os.getenv('FLASK_ENV') == 'production':
    CORS(app, origins=os.getenv('CORS_ORIGINS', '*').split(','))
else:
    CORS(app)  # Development - allow all origins

# Security configuration
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Logging yapılandırması
log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'app.log')),
        logging.StreamHandler()
    ]
)
app.logger.setLevel(log_level)

# Configuration from environment variables
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
APPIFY_TOKEN = os.getenv('APPIFY_TOKEN')
RAPIDAPI_YOUTUBE_DOWNLOADER = os.getenv('RAPIDAPI_YOUTUBE_DOWNLOADER', 'https://youtube-media-downloader.p.rapidapi.com/v2/video/details')
APPIFY_YOUTUBE_DOWNLOADER = os.getenv('APPIFY_YOUTUBE_DOWNLOADER', 'https://api.apify.com/v2/acts/streamers~youtube-video-downloader/runs')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
MAX_WAIT_TIME = int(os.getenv('MAX_WAIT_TIME', 300))
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Validate required environment variables
if not RAPIDAPI_KEY or not APPIFY_TOKEN:
    app.logger.warning("UYARI: RAPIDAPI_KEY veya APPIFY_TOKEN environment variable'ları ayarlanmamış!")
    if os.getenv('FLASK_ENV') == 'production':
        raise ValueError("Production ortamında API anahtarları gereklidir!")

# İndirme durumlarını takip etmek için
download_tasks = {}

class DownloadProgress:
    def __init__(self, task_id):
        self.task_id = task_id
        self.progress = 0
        self.status = 'starting'
        self.message = 'İndirme başlatılıyor...'
        self.filename = None
        self.download_url = None
        self.error = None
        self.created_at = time.time()

    def update(self, progress=None, status=None, message=None, filename=None, download_url=None, error=None):
        if progress is not None:
            self.progress = progress
        if status is not None:
            self.status = status
        if message is not None:
            self.message = message
        if filename is not None:
            self.filename = filename
        if download_url is not None:
            self.download_url = download_url
        if error is not None:
            self.error = error

def extract_video_id(url):
    """YouTube URL'sinden video ID'sini çıkar"""
    import re
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/|v\/|youtu\.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_info_rapidapi(url):
    """RapidAPI ile video bilgilerini al"""
    video_id = extract_video_id(url)
    if not video_id:
        if DEBUG_MODE:
            print("Geçersiz YouTube URL")
        return None
        
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': 'youtube-media-downloader.p.rapidapi.com'
    }
    
    params = {'videoId': video_id}
    
    try:
        if DEBUG_MODE:
            app.logger.info(f"RapidAPI isteği gönderiliyor: {RAPIDAPI_YOUTUBE_DOWNLOADER}")
            app.logger.info(f"Video ID: {video_id}")
            
        response = requests.get(RAPIDAPI_YOUTUBE_DOWNLOADER, headers=headers, params=params, timeout=API_TIMEOUT)
        
        if DEBUG_MODE:
            app.logger.info(f"RapidAPI yanıt kodu: {response.status_code}")
            app.logger.info(f"RapidAPI yanıt: {response.text[:500]}...")  # İlk 500 karakter
            
        if response.status_code == 200:
            json_response = response.json()
            if DEBUG_MODE:
                app.logger.info(f"JSON keys: {list(json_response.keys()) if isinstance(json_response, dict) else 'Not a dict'}")
            return json_response
        else:
            if DEBUG_MODE:
                app.logger.error(f"RapidAPI HTTP hatası: {response.status_code}")
                app.logger.error(f"Response: {response.text}")
            return None
    except Exception as e:
        if DEBUG_MODE:
            app.logger.error(f"RapidAPI hatası: {e}")
        return None

def start_apify_download(url, format_type, quality):
    """Apify ile indirme başlat"""
    headers = {
        'Content-Type': 'application/json'
    }
    
    input_data = {
        "videos": [{
            "url": url
        }],
        "format": format_type,
        "quality": quality
    }
    
    try:
        apify_url = f"{APPIFY_YOUTUBE_DOWNLOADER}?token={APPIFY_TOKEN}"
        response = requests.post(apify_url, headers=headers, json=input_data, timeout=API_TIMEOUT)
        
        if response.status_code == 201:
            return response.json()
        else:
            if DEBUG_MODE:
                print(f"Apify HTTP hatası: {response.status_code}")
            return None
    except Exception as e:
        if DEBUG_MODE:
            print(f"Apify hatası: {e}")
        return None

def check_apify_status(run_id):
    """Apify run durumunu kontrol et"""
    try:
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}?token={APPIFY_TOKEN}"
        response = requests.get(status_url, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            return response.json()
        else:
            if DEBUG_MODE:
                print(f"Apify durum kontrolü HTTP hatası: {response.status_code}")
            return None
    except Exception as e:
        if DEBUG_MODE:
            print(f"Apify durum kontrolü hatası: {e}")
        return None

def get_apify_results(run_id):
    """Apify sonuçlarını al"""
    try:
        results_url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APPIFY_TOKEN}"
        response = requests.get(results_url, timeout=API_TIMEOUT)
        
        if response.status_code == 200:
            return response.json()
        else:
            if DEBUG_MODE:
                print(f"Apify sonuç alma HTTP hatası: {response.status_code}")
            return None
    except Exception as e:
        if DEBUG_MODE:
            print(f"Apify sonuç alma hatası: {e}")
        return None

def download_video(url, format_type, quality, task_id):
    """Online API ile video indirme fonksiyonu"""
    try:
        task = download_tasks[task_id]
        task.update(status='processing', message='Video bilgileri alınıyor...')
        
        # Önce RapidAPI ile video bilgilerini almayı dene
        video_info = get_video_info_rapidapi(url)
        
        if video_info and 'title' in video_info:
            title = video_info.get('title', 'video')
            task.update(status='processing', message=f'Video bulundu: {title}')
            
            # RapidAPI'den direkt indirme linklerini kontrol et
            if 'videos' in video_info and 'items' in video_info['videos']:
                links = video_info['videos']['items']
                
                # Format ve kaliteye göre uygun linki bul
                download_link = None
                filename = f"{title}.{format_type}"
                
                if format_type == 'mp3':
                    # MP3 için ses linklerini ara (hasAudio=true olanları)
                    for link in links:
                        if link.get('hasAudio', False) and 'mp4' in link.get('extension', ''):
                            download_link = link.get('url')
                            break
                else:
                    # MP4 için video linklerini ara
                    for link in links:
                        if link.get('hasAudio', True):  # Ses içeren video dosyaları
                            if quality == 'best' or quality in link.get('quality', ''):
                                if 'mp4' in link.get('extension', ''):
                                    download_link = link.get('url')
                                    break
                
                if download_link:
                    task.update(progress=100, status='completed', 
                              message='İndirme linki hazır!', 
                              filename=filename, download_url=download_link)
                    return
        
        # RapidAPI başarısız olursa Apify'ı dene
        task.update(status='processing', message='Alternatif servis deneniyor...')
        
        apify_result = start_apify_download(url, format_type, quality)
        
        if apify_result and 'data' in apify_result:
            run_id = apify_result['data']['id']
            task.update(status='processing', message='İndirme işlemi başlatıldı...')
            
            # Apify işleminin tamamlanmasını bekle
            wait_interval = 10   # 10 saniye
            waited_time = 0
            
            while waited_time < MAX_WAIT_TIME:
                time.sleep(wait_interval)
                waited_time += wait_interval
                
                progress = min(90, (waited_time / MAX_WAIT_TIME) * 90)
                task.update(progress=progress, status='processing', 
                          message=f'İşleniyor... {progress:.0f}%')
                
                status_result = check_apify_status(run_id)
                
                if status_result and status_result.get('data', {}).get('status') == 'SUCCEEDED':
                    # Sonuçları al
                    results = get_apify_results(run_id)
                    
                    if results and len(results) > 0:
                        result = results[0]
                        download_url = result.get('downloadUrl')
                        filename = result.get('filename', f'video.{format_type}')
                        
                        if download_url:
                            task.update(progress=100, status='completed',
                                      message='İndirme tamamlandı!',
                                      filename=filename, download_url=download_url)
                            return
                    break
                elif status_result and status_result.get('data', {}).get('status') == 'FAILED':
                    raise Exception('İndirme işlemi başarısız oldu')
            
            if waited_time >= MAX_WAIT_TIME:
                raise Exception('İndirme işlemi zaman aşımına uğradı')
        
        # Her iki API de başarısız olursa
        raise Exception('Video indirilemedi. Lütfen daha sonra tekrar deneyin.')
        
    except Exception as e:
        error_msg = str(e)
        if 'api key' in error_msg.lower():
            error_msg = 'API anahtarı geçersiz. Lütfen ayarları kontrol edin.'
        elif 'private' in error_msg.lower():
            error_msg = 'Bu video özel veya kısıtlı.'
        elif 'not available' in error_msg.lower():
            error_msg = 'Video mevcut değil veya kaldırılmış.'
        elif 'quota' in error_msg.lower():
            error_msg = 'API kullanım limitine ulaşıldı.'
        
        download_tasks[task_id].update(status='failed', error=error_msg)

@app.route('/api/download', methods=['POST'])
def start_download():
    """İndirme başlatma endpoint'i"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL gerekli'}), 400
        
        url = data['url']
        format_type = data.get('format', 'mp4')
        quality = data.get('quality', 'best')
        
        # URL doğrulama
        youtube_regex = r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+'
        if not re.match(youtube_regex, url):
            return jsonify({'error': 'Geçerli bir YouTube URL\'si değil'}), 400
        
        # Benzersiz task ID oluştur
        task_id = str(uuid.uuid4())
        
        # Task oluştur
        download_tasks[task_id] = DownloadProgress(task_id)
        
        # Arka planda indirme başlat
        thread = threading.Thread(target=download_video, args=(url, format_type, quality, task_id))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'İndirme başlatıldı'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def get_download_status(task_id):
    """İndirme durumu kontrolü"""
    if task_id not in download_tasks:
        return jsonify({'error': 'Geçersiz task ID'}), 404
    
    task = download_tasks[task_id]
    
    response = {
        'status': task.status,
        'progress': task.progress,
        'message': task.message
    }
    
    if task.status == 'completed':
        response['download_url'] = task.download_url  # Direkt online URL
        response['filename'] = task.filename
    elif task.status == 'failed':
        response['error'] = task.error
    
    return jsonify(response)

@app.route('/api/download-file/<task_id>', methods=['GET'])
def download_file(task_id):
    """Online dosya indirme redirect endpoint'i"""
    if task_id not in download_tasks:
        return jsonify({'error': 'Geçersiz task ID'}), 404
    
    task = download_tasks[task_id]
    
    if task.status != 'completed' or not task.download_url:
        return jsonify({'error': 'Dosya hazır değil'}), 400
    
    try:
        # Online URL'ye redirect et
        return redirect(task.download_url)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sağlık kontrolü"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_downloads': len([t for t in download_tasks.values() if t.status in ['downloading', 'processing']])
    })

@app.route('/api/proxy-download', methods=['POST'])
def proxy_download():
    """Dosya indirme proxy endpoint'i - CORS sorununu çözer"""
    try:
        data = request.get_json()
        download_url = data.get('download_url')
        
        if not download_url:
            return jsonify({'error': 'download_url gerekli'}), 400
            
        # Dosyayı indir
        response = requests.get(download_url, stream=True, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'error': 'Dosya indirilemedi'}), 400
            
        # Content-Type'ı belirle
        content_type = response.headers.get('content-type', 'application/octet-stream')
        
        # Dosya boyutunu al
        content_length = response.headers.get('content-length')
        
        # Response oluştur
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        flask_response = Response(generate(), content_type=content_type)
        
        if content_length:
            flask_response.headers['Content-Length'] = content_length
            
        # CORS headers ekle
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        flask_response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        flask_response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return flask_response
        
    except Exception as e:
        if DEBUG_MODE:
            app.logger.error(f"Proxy download hatası: {e}")
        return jsonify({'error': 'Proxy indirme hatası'}), 500

def cleanup_old_tasks():
    """Eski task'ları temizle"""
    try:
        current_time = time.time()
        max_task_age = 3600  # 1 saat
        
        tasks_to_remove = []
        for task_id, task in download_tasks.items():
            if hasattr(task, 'created_at'):
                if current_time - task.created_at > max_task_age:
                    tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del download_tasks[task_id]
            print(f"Eski task silindi: {task_id}")
            
    except Exception as e:
        print(f"Task temizleme hatası: {e}")

# Periyodik temizlik
def periodic_cleanup():
    while True:
        time.sleep(1800)  # 30 dakikada bir
        cleanup_old_tasks()

# Temizlik thread'ini başlat
cleanup_thread = threading.Thread(target=periodic_cleanup)
cleanup_thread.daemon = True
cleanup_thread.start()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Basic health checks
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'active_tasks': len(download_tasks),
            'environment': os.getenv('FLASK_ENV', 'development')
        }
        
        # Check if API keys are configured
        if not RAPIDAPI_KEY or not APPIFY_TOKEN:
            status['warnings'] = ['API keys not configured']
            
        return jsonify(status), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'Dosya çok büyük'}), 413

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Çok fazla istek. Lütfen bekleyin.'}), 429

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Sunucu hatası'}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print("YouTube Dönüştürücü Backend Başlatılıyor...")
    print(f"API Endpoint: http://{host}:{port}/api")
    print(f"Sağlık Kontrolü: http://{host}:{port}/api/health")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(debug=debug, host=host, port=port)
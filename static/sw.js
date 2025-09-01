const CACHE_NAME = 'youtube-converter-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/style.css',
    '/script.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Service Worker kurulumu
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache açıldı');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch olayları
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache'de varsa cache'den döndür
                if (response) {
                    return response;
                }
                // Yoksa network'ten al
                return fetch(event.request);
            }
        )
    );
});
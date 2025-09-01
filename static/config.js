// Configuration for GitHub Pages deployment
const CONFIG = {
    // Backend URL - will be replaced during GitHub Actions deployment
    BACKEND_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:5000' 
        : 'https://your-backend-service.herokuapp.com',
    
    // API endpoints
    API_ENDPOINTS: {
        DOWNLOAD: '/api/download',
        STATUS: '/api/status',
        PROXY_DOWNLOAD: '/api/proxy-download',
        HEALTH: '/api/health'
    },
    
    // App settings
    SETTINGS: {
        MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
        POLL_INTERVAL: 1000, // 1 second
        MAX_RETRIES: 3
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
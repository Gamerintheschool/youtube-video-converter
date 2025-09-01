#!/bin/bash

# Production start script for YouTube Converter

set -e

echo "Starting YouTube Converter in production mode..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys."
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$RAPIDAPI_KEY" ] || [ -z "$APPIFY_TOKEN" ]; then
    echo "Error: Required API keys not found in .env file!"
    echo "Please set RAPIDAPI_KEY and APPIFY_TOKEN in your .env file."
    exit 1
fi

# Create downloads directory if it doesn't exist
mkdir -p downloads

# Set default values if not provided
export FLASK_ENV=${FLASK_ENV:-production}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-5000}
export WORKERS=${WORKERS:-4}
export TIMEOUT=${TIMEOUT:-120}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

echo "Configuration:"
echo "  Environment: $FLASK_ENV"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Timeout: $TIMEOUT seconds"
echo "  Log Level: $LOG_LEVEL"
echo ""

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn \
    --bind $HOST:$PORT \
    --workers $WORKERS \
    --timeout $TIMEOUT \
    --log-level $LOG_LEVEL \
    --access-logfile - \
    --error-logfile - \
    --preload \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    app:app
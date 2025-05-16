#!/bin/bash
set -e

# Initialize variables
MEMORY_LIMIT=${MEMORY_LIMIT:-512}
WORKER_COUNT=${MAX_WORKERS:-1}
THREAD_COUNT=${WORKER_THREADS:-2}

echo "Starting NexusAI with memory optimization..."
echo "Memory limit: ${MEMORY_LIMIT}MB"
echo "Worker count: ${WORKER_COUNT}"
echo "Thread count: ${THREAD_COUNT}"

# Perform garbage collection on SIGTERM
trap 'echo "Received SIGTERM, gracefully shutting down..."; pkill -f gunicorn; exit 0' SIGTERM

# Set Python garbage collection thresholds
export PYTHONHASHSEED=random
export PYTHONGC=1

# Memory optimization
echo "Applying memory optimizations..."
export MALLOC_TRIM_THRESHOLD_=100000
export PYTHONMALLOC=malloc

# Start Gunicorn with proper settings
exec gunicorn --bind 0.0.0.0:${PORT:-8080} \
    --workers $WORKER_COUNT \
    --threads $THREAD_COUNT \
    --timeout 120 \
    --max-requests 100 \
    --max-requests-jitter 20 \
    --worker-tmp-dir /dev/shm \
    --preload \
    --graceful-timeout 30 \
    app:app 
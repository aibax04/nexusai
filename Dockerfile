# Use Python 3.10 slim base image
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Second stage - smaller final image
FROM python:3.10-slim

WORKDIR /app

# Set environment variables for runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Memory optimization settings
ENV MALLOC_TRIM_THRESHOLD_=100000
# Limit Python memory usage
ENV PYTHONMALLOC=malloc
# Disable JIT for memory savings
ENV NUMBA_DISABLE_JIT=1

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install additional utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary application files
COPY app.py .
COPY templates/ templates/
COPY start.sh .
RUN chmod +x start.sh

# Expose port
EXPOSE 8080

# Pre-download models to avoid memory spikes during first request
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Command to run the app with our start script
CMD ["./start.sh"]



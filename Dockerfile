# DeepGuard Flask App - Docker Image
# ===================================
# Optimized for inference (CPU only)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set pip timeout and retries (fixes timeout issues with large packages)
ENV PIP_DEFAULT_TIMEOUT=300
ENV PIP_RETRIES=5

# Copy requirements first (for better caching)
COPY flask_app/requirements.txt ./flask_app/

# Install dependencies with extended timeout
RUN pip install --no-cache-dir --timeout 300 -r flask_app/requirements.txt

# Copy application code
COPY flask_app/ ./flask_app/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=flask_app/app.py
ENV FLASK_ENV=production
ENV TF_CPP_MIN_LOG_LEVEL=2

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

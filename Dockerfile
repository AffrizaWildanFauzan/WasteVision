FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua kode
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Buat folder uploads
RUN mkdir -p ./backend/uploads/images
RUN mkdir -p ./backend/uploads/results
RUN mkdir -p ./backend/model

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

# Bagian paling krusial!
WORKDIR /app
CMD ["python", "backend/app.py"]

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (diperbaiki)
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
COPY notebooks/ ./notebooks/

# Buat folder uploads
RUN mkdir -p /app/backend/uploads/images
RUN mkdir -p /app/backend/uploads/results
RUN mkdir -p /app/backend/model

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

WORKDIR /app/backend

EXPOSE 5000

# Start aplikasi
CMD ["python", "app.py"]

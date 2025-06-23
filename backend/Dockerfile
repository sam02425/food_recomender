FROM python:3.11-slim

# Install system dependencies for dlib, face-recognition, and opencv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create logs directory with proper permissions
RUN mkdir -p /app/logs/backend && \
    chmod -R 777 /app/logs

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure logs directory is writable after copying files
RUN chmod -R 777 /app/logs

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
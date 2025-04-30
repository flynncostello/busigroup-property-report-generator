# Use Python slim image instead of Miniconda for better compatibility
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install WeasyPrint system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    fonts-freefont-ttf \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code 
COPY . .

# Create necessary directories
RUN mkdir -p uploads output logs static/images static/css static/js templates

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=8000

# Expose port (ensure it matches PORT env var)
EXPOSE 8000

# Simplified startup command without fallback to tail
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app", "--log-level=info", "--timeout=120"]
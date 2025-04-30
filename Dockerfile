# Start from Miniconda3 (lightweight Conda Python base)
FROM continuumio/miniconda3

# Set working directory inside the container
WORKDIR /app

# Install WeasyPrint system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    fonts-freefont-ttf \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy your app code into the container
COPY . .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install flask werkzeug jinja2 gunicorn pandas openpyxl numpy openpyxl-image-loader beautifulsoup4 weasyprint

# Create folders needed by app (uploads, output, etc.)
RUN mkdir -p uploads output logs static/images static/css static/js templates

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 8000

# Start the app with Gunicorn directly
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
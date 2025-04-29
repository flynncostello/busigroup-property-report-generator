# Start from Miniconda3 (lightweight Conda Python base)
FROM continuumio/miniconda3

# Set working directory inside the container
WORKDIR /app

# Install WeasyPrint system dependencies (VERY important!)
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

# Make your start.sh executable
RUN chmod +x start.sh

# Set environment variable so start.sh knows it's inside Docker
ENV RUNNING_IN_DOCKER=true

# Expose port 8000 to outside
EXPOSE 8000

# Run the setup and app launcher
CMD ["./start.sh"]
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Create necessary folders and set permissions
RUN mkdir -p /app/output /app/uploads /app/logs && \
    chmod -R 777 /app/output /app/uploads /app/logs

# Install WeasyPrint system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    libpango1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    git \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy application code into the container
COPY . .

# Make important scripts executable
RUN chmod +x setup.sh start.sh keepalive.py

# Activate conda and run setup.sh to create environment
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && bash setup.sh"

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=False

# Expose necessary ports
EXPOSE 8000 8001

# Command to run at container start
CMD ["/bin/bash", "./start.sh"]

# Healthcheck to ensure app is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

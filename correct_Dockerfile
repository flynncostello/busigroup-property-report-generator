FROM continuumio/miniconda3

WORKDIR /app

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
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY . .

# Make scripts executable
RUN chmod +x setup.sh
RUN chmod +x start.sh

# Activate conda, run setup.sh (which creates and installs into reportgen env)
SHELL ["/bin/bash", "-c"]
RUN source /opt/conda/etc/profile.d/conda.sh && bash setup.sh

# Environment vars
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=False

# Use PORT environment variable with fallback to 8000
EXPOSE 8000

# Use a startup script that respects PORT env variable
CMD ["/bin/bash", "./start.sh"]

HEALTHCHECK CMD curl --fail http://localhost:8000 || exit 1
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

# Make script executable
RUN chmod +x setup.sh

# Skip Homebrew section at runtime, not by modifying the file
RUN bash -c 'source setup.sh || true'

# Set env vars
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=False

EXPOSE 8000

CMD ["bash", "-c", "source $(conda info --base)/etc/profile.d/conda.sh && conda activate reportgen && gunicorn app:app --bind 0.0.0.0:8000"]

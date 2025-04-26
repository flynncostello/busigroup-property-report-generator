FROM python:3.10-slim

WORKDIR /app

# Install Flask
RUN pip install flask gunicorn

# Copy minimal files
COPY app.py .
COPY start.sh .

# Make script executable
RUN chmod +x start.sh

ENV PORT=8000
EXPOSE 8000

# Extremely simple startup
CMD ["/bin/bash", "./start.sh"]
# Start with a slim Python base image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy only requirements first (for faster caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Set environment variables
ENV PORT=8000

# Expose port
EXPOSE 8000

# Define the startup command
CMD ["./start.sh"]

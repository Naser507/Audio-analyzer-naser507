# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/
COPY tmp/ /app/tmp/

# Set working directory to backend
WORKDIR /app/backend

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]

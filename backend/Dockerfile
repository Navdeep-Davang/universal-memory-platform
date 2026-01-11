FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ ./src/

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# Using uvicorn with host 0.0.0.0 for container accessibility
CMD ["uvicorn", "src.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]

# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PYTHONPATH=/app

WORKDIR /app

# Install system dependencies required for psycopg2 compilation and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libpq-dev     curl     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip &&     pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY . .

# Ensure directory for SQLite database storage exists
RUN mkdir -p /app/data

# Expose default FastAPI port
EXPOSE 8000

# Run API server with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

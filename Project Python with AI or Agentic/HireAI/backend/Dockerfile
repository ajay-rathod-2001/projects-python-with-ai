# Production Dockerfile for HireAI Backend
FROM python:3.11-slim

# Install system dependencies for document parsing and C/C++ compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    tesseract-ocr \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pyjwt psycopg2-binary redis celery

# Copy backend application source
COPY . .

# Create storage directories
RUN mkdir -p /app/storage/resumes /app/storage/job_descriptions /app/storage/reports /app/storage/submissions

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

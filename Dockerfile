# Use official Python 3.13 slim image
FROM python:3.13-slim

# Prevents Python from writing .pyc files and buffers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps (if needed) and system deps for libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt ./

# Install Python deps
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy source
COPY ./src ./src

# Expose the port the app will run on
EXPOSE 8000

# Use a non-root user for security
USER app

# Default command to run the FastAPI app with uvicorn
CMD ["uvicorn", "job_hunting.entrypoints.api:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]


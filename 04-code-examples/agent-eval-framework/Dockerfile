# Agent Evaluation Framework - Containerized Runner
# Used for reproducible evaluation environments and CI/CD.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy framework code
COPY . .

# Default: run the full evaluation suite
CMD ["pytest", "tests/", "-v", "--tb=short"]

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Make scripts executable
RUN chmod +x scripts/*.py

# Set Python path
ENV PYTHONUNBUFFERED=1

CMD ["bash"]

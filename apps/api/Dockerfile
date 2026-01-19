FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including pg-client for DB debugging)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first
COPY pyproject.toml . 
# If you have a requirements.txt or poetry.lock, copy that too
# COPY requirements.txt . 

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy the rest of the app
COPY . .

EXPOSE 8000

# Start with --reload for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
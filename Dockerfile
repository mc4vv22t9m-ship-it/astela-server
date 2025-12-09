FROM python:3.9-slim

# Install system dependencies needed by swisseph (Swiss Ephemeris)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0 \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server.py .

# Railway će nam dati PORT kroz env var, a server.py ga već čita
ENV PYTHONUNBUFFERED=1

CMD ["python", "server.py"]

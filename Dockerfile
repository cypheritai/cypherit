FROM python:3.11-slim

WORKDIR /app

# Install CA certificates for SSL
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir certifi -r requirements.txt

# Copy backend
COPY backend/ ./backend/

# Copy frontend
COPY frontend/ ./frontend/

# Set environment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV SSL_CERT_FILE=/usr/local/lib/python3.11/site-packages/certifi/cacert.pem
ENV REQUESTS_CA_BUNDLE=/usr/local/lib/python3.11/site-packages/certifi/cacert.pem

# Run
CMD ["python", "backend/main.py"]

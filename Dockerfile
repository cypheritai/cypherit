FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ ./backend/

# Set environment
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run
CMD ["python", "backend/main.py"]

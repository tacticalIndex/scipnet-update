FROM python:3.11-slim

WORKDIR /app

# System deps for some python packages (adjust as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure unbuffered output for logs
ENV PYTHONUNBUFFERED=1

# Use PORT env var provided by Render
ENV PORT=8000

# Start uvicorn serving the combined FastAPI + Discord bot ASGI app
CMD ["uvicorn", "asgi_app:app", "--host", "0.0.0.0", "--port", "${PORT}"]
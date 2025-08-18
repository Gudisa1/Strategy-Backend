# Stage 1: Build environment
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Install dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .


# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Production
FROM python:3.11-slim

WORKDIR /usr/src/app

# Install system dependencies in prod
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*


# Copy from builder
COPY --from=builder /usr/src/app .
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000

# Start the app and wait for Postgres
CMD sh -c '\
    echo "Waiting for postgres..."; \
    while ! nc -z db 5432; do sleep 0.1; done; \
    echo "Postgres started!"; \
    python manage.py migrate --noinput; \
    python manage.py collectstatic --noinput; \
    exec gunicorn --bind 0.0.0.0:8000 strategybackend.wsgi:application \
'

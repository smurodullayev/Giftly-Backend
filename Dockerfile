FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Tizim kutubxonalari
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Avval requirements — Docker cache'dan foydalanish uchun
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Static fayllarni yig'ish (prod)
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

# Prod: gunicorn. Dev: docker-compose da override qilinadi.
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

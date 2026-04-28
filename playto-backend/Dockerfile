FROM python:3.12-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .


RUN pip install --upgrade pip
RUN pip install "setuptools<70"
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

RUN python manage.py collectstatic --noinput || true

# Default command
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "payout_engine.asgi:application"]

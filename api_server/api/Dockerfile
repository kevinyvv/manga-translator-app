# syntax=docker/dockerfile:1

# --- Base image ---
FROM python:3.13-slim AS base

# Prevents Python from writing .pyc files and enables unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Install system dependencies and poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
 && curl -sSL https://install.python-poetry.org | python3 - \
 && mv /root/.local/bin/poetry /usr/local/bin/ \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Dependencies layer ---
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --no-interaction --no-ansi

# --- Application code ---
COPY . .

# --- Runtime command ---
# Use Hypercorn in production (faster & better concurrency than app.run)
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "4"]

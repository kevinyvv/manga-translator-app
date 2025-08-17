# Use an official Python base image (match your local version, e.g., 3.13 if that's what you use)
FROM python:3.13-slim

# Set environment variables
ENV POETRY_VERSION=1.8.2 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the backend code
COPY . .

# Expose the port (adjust if your app uses a different port)
EXPOSE 5000

# Set the entrypoint (adjust if your main file is not app.py)
CMD ["python", "app.py"]

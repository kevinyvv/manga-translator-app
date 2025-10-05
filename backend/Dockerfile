FROM python:3.13-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*


ENV POETRY_VERSION=2.1.3 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_CREATE=false

# Set work directory
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN poetry install --no-interaction --no-ansi \
    && poetry cache clear . --all -n 

RUN pip uninstall -y torch torchvision torchaudio && \
    pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cpu

# Copy the rest of the backend code
COPY . .

# Expose the port (adjust if your app uses a different port)
EXPOSE 5000

# Set the entrypoint (adjust if your main file is not app.py)
CMD ["poetry", "run", "python3", "app.py"]

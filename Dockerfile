FROM python:3.13-slim

WORKDIR /app

# Install system dependencies needed for compiling certain python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging files first
COPY pyproject.toml /app/

# Install dependencies (ignoring the actual package installed later)
# We can do this correctly using pip
RUN pip install --no-cache-dir build && pip install setuptools

# Just copy the whole project
COPY . /app/

# Install the project
RUN pip install --no-cache-dir -e .

# Install Playwright browsers and their system dependencies
RUN playwright install --with-deps chromium

# Define the entrypoint so it acts as a CLI
ENTRYPOINT ["python", "main.py"]

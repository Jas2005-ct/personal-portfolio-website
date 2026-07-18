# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock* /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . /app/

# Build Tailwind CSS, collect static files, and prepare the database
ENV SECRET_KEY=build-time-secret-key-not-for-production
ENV DEBUG=true
RUN cd theme/static_src && npm ci && npm run build && cd ../..
RUN python manage.py collectstatic --no-input

# Expose the port
EXPOSE 8000

# Apply migrations, then start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --no-input && gunicorn project.wsgi:application --bind 0.0.0.0:${PORT}"]

# Stage 1: Builder - Install dependencies
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Copy pyproject.toml
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir .

# ---

# Stage 2: Runner - Setup the final image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the application source code
COPY ./app ./app
COPY ./assets ./assets
COPY ./scripts ./scripts

# Data import scripts will be run at container startup to avoid conflicts with the volume

# Change ownership of the app files to the app user
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Declare a volume for the database to persist data
VOLUME /app/data

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application and import data at startup
# Use 0.0.0.0 to make it accessible from outside the container
CMD bash -c 'export DB_URL="sqlite+aiosqlite:///app/data/database.db" \
    && python scripts/import_careers_from_yaml.py \
    && python scripts/import_quiz_from_yaml.py \
    && uvicorn app.main:app --host 0.0.0.0 --port 8080'

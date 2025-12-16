# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final runtime image
FROM python:3.11-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Create user and set working directory
RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser --exclude=.venv --exclude=*.pyc --exclude=.env parser_domclick parser_domclick

# Disable bytecode generation and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set user and run the application
USER appuser

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "parser_domclick.app:app", "--host", "0.0.0.0", "--port", "8000"]

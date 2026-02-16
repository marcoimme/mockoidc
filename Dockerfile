# Mock OIDC Server - Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="Mock OIDC Server"
LABEL description="Mock OpenID Connect Provider for testing and development"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8080

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files first for better caching
COPY pyproject.toml .
COPY .python-version .

# Install Python dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy application files
COPY main.py .
COPY config.py .
COPY models.py .
COPY token_service.py .
COPY jwks_service.py .
COPY claims_generator.py .
COPY .env.example .env

# Create non-root user for security
RUN useradd -m -u 1000 oidc && \
    chown -R oidc:oidc /app

# Switch to non-root user
USER oidc

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "main.py"]

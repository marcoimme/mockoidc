# Mock OIDC Server - Dockerfile
# Build stage
FROM python:3.13-slim AS py-build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build dependencies for compiling Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy dependency files and README (required by hatchling)
COPY pyproject.toml uv.lock* README.md ./

# Install dependencies in virtual environment
RUN uv sync --locked --no-dev || uv sync --no-dev

# Copy application files
COPY main.py config.py models.py token_service.py jwks_service.py claims_generator.py ./
COPY .env.example .env

# Final stage
FROM python:3.13-slim

# Metadata
LABEL maintainer="Mock OIDC Server"
LABEL description="Mock OpenID Connect Provider for testing and development"
LABEL version="1.0.0"

# Install wget for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8080 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy virtual environment and application from build stage
COPY --from=py-build /app/.venv /app/.venv
COPY --from=py-build /app/*.py /app/
COPY --from=py-build /app/.env /app/.env

# Create non-root user for security
RUN groupadd -g 1000 oidc && \
    useradd -m -u 1000 -g oidc oidc && \
    chown -R oidc:oidc /app

# Switch to non-root user
USER oidc

# Expose port
EXPOSE 8080

# Health check (using wget, already available in Alpine)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application
CMD ["python", "main.py"]

# Mock OIDC Server - Dockerfile
# Build stage
FROM python:3.12-alpine AS py-build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Copy dependency files and README (required by hatchling)
COPY pyproject.toml uv.lock* README.md ./

# Install dependencies (sync from lock file if exists, otherwise resolve and install)
RUN uv sync --locked --no-dev || uv sync --no-dev

# Copy application files
COPY main.py config.py models.py token_service.py jwks_service.py claims_generator.py ./
COPY .env.example .env

# Final stage
FROM python:3.12-alpine

# Metadata
LABEL maintainer="Mock OIDC Server"
LABEL description="Mock OpenID Connect Provider for testing and development"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8080

WORKDIR /app

# Copy application and dependencies from build stage
COPY --from=py-build /app /app
COPY --from=py-build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Create non-root user for security (Alpine syntax)
RUN addgroup -g 1000 oidc && \
    adduser -D -u 1000 -G oidc oidc && \
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

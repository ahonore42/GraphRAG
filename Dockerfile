FROM python:3.12.4-alpine

# Install uv
RUN apk add --no-cache curl tar && \
    curl -LO https://github.com/astral-sh/uv/releases/download/0.1.35/uv-x86_64-unknown-linux-musl.tar.gz && \
    tar -xzf uv-x86_64-unknown-linux-musl.tar.gz && \
    mv uv-x86_64-unknown-linux-musl/uv /usr/local/bin/uv && \
    rm -rf uv-x86_64-unknown-linux-musl.tar.gz uv-x86_64-unknown-linux-musl

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup && \
    apk add --no-cache curl

# Set up application directory
WORKDIR /app
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Create virtual environment
RUN uv venv

# Copy project files
COPY --chown=appuser:appgroup pyproject.toml ./

# Install dependencies
RUN uv pip sync pyproject.toml

# Copy application code
COPY --chown=appuser:appgroup . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Set default command, but allow override
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

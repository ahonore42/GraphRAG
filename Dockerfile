FROM python:3.13.5-alpine

# Install latest version of uvicorn
COPY --from=ghcr.io/astral-sh/latest /uv /uvx /usr/local/bin/

# Set uv version to match python version
RUN uv venv 3.13.5

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup && \
    apk add --no-cache curl

# Set up application directory
WORKDIR /app
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Copy project files
COPY --chown=appuser:appgroup pyproject.toml ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY --chown=appuser:appgroup . .

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

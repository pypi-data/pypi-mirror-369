# Use official uv image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Build argument for version
ARG VERSION=0.0.0+dev

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}

# Create app directory
WORKDIR /app

# Install gosu for user switching and curl for healthchecks
RUN apt-get update && apt-get install -y gosu curl && rm -rf /var/lib/apt/lists/* && \
    groupadd -g 1000 appuser && \
    useradd --create-home --no-log-init -u 1000 -g 1000 appuser

# Copy dependency files and README
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Create directory for temporary files and set ownership
RUN mkdir -p /tmp/subtitles && \
    chown -R appuser:appuser /app /tmp/subtitles

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port (non-privileged port for non-root user)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set entrypoint and default command
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uv", "run", "fastapi", "run", "src/ai_subtitle_translator/app.py", "--host", "0.0.0.0", "--port", "8080"]
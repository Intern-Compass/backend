FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

#Setting working directory for container
WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN uv sync --frozen --no-cache

COPY . .

# Expose FastAPI port
EXPOSE 8000

# Set environment variable for templates
#ENV TEMPLATE_DIR=/app/src/templates

# Start the app using uv and uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

#Setting working directory for container
WORKDIR /app

COPY uv.lock .
COPY pyproject.toml .

RUN uv sync --frozen --no-cache

COPY . .

# Expose FastAPI port
EXPOSE 8000


# Start the app using uv and uvicorn
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
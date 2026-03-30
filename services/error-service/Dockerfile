FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

WORKDIR /app

COPY pyproject.toml /app/
RUN uv sync

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 5002

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5002", "main:app"]

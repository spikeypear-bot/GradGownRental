FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
WORKDIR /app/src

EXPOSE 5005
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "app:app", "--workers", "1", "--threads", "8"]

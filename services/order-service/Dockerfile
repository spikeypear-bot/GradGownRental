FROM python:3.13-slim

WORKDIR /app
RUN apt-get update && apt-get install -y dos2unix && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN dos2unix /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8081

ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]

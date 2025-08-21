FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements из корня
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы worker
COPY worker/worker.py .

# Копируем общие файлы из корня
COPY rabbitmq.py .
COPY ml_model/ ./ml_model/
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

ENV PYTHONPATH=/app

CMD ["/wait-for-db.sh", "database", "python", "worker.py"]
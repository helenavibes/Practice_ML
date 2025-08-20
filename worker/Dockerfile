FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода воркера и модели
COPY worker.py .
COPY ml_model/ ./ml_model/
COPY rabbitmq.py .

# Копирование скрипта ожидания БД и установка прав
COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

# Переменные окружения
ENV PYTHONPATH=/app

# Команда запуска
CMD ["/wait-for-db.sh", "database", "python", "worker.py"]
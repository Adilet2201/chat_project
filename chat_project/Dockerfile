# Используем python:3.12-slim как базовый образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Скопируем requirements и установим
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем всё содержимое проекта (manage.py, приложение и т.д.)
COPY . /app

# По умолчанию запускаем gunicorn (или можно оставить cmd пустым и прописать в docker-compose)
CMD ["gunicorn", "chat_project.wsgi:application", "--bind", "0.0.0.0:8000"]

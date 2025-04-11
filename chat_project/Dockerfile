# Use Python 3.12 but keep the same structure
FROM python:3.12-slim

WORKDIR /app

# System libs for psycopg2‑binary, Pillow


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
# Collect static at build time so Nginx can serve it immediately
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "chat_project.wsgi:application", "--bind", "0.0.0.0:8000"]

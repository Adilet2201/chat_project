# Use the official Python image based on slim for a lightweight container.
FROM python:3.12-slim

# Set environment variables to avoid .pyc files and enable unbuffered output.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory in the container.
WORKDIR /app

# Install system dependencies.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies.
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the container.
COPY . /app/

# Collect static files (optional, only if you use them in production)
# RUN python manage.py collectstatic --noinput

# Expose port 8000 for the Django development server.
EXPOSE 8000

# Start the Django development server.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

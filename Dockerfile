# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . /app/

# Optional: collect static files (uncomment if needed)
# RUN python manage.py collectstatic --noinput

# Run migrations and start the app
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && gunicorn mrsafe_project.wsgi:application --bind 0.0.0.0:8000"]

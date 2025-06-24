# Use an official Python runtime as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . /app/

# Run Django collectstatic if needed
# RUN python manage.py collectstatic --noinput

# Run the application using gunicorn
CMD ["gunicorn", "mrsafe.wsgi:application", "--bind", "0.0.0.0:8000"]

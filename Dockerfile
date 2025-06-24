# Use an official Python runtime as a base image
FROM python:3.12  # Change if needed

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    python3-dev \
    gcc \
    libpq-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    libportaudio2

# Create and activate a virtual environment
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip

# Copy project files
COPY . /app

# Install project dependencies
RUN pip install -r requirements.txt

# Expose the application port
EXPOSE 8000

# Default command to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "quiz_project.wsgi:application"]

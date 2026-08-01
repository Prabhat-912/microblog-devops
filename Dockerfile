# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose Flask/Gunicorn port
EXPOSE 5000

# Run app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
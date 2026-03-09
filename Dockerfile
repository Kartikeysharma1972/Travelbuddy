FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port (7860 for Hugging Face Spaces)
EXPOSE 7860

# Run gunicorn with memory-optimized settings for Hugging Face Spaces
CMD ["gunicorn", \
     "--bind", "0.0.0.0:7860", \
     "--workers", "1", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--timeout", "60", \
     "app:app"]
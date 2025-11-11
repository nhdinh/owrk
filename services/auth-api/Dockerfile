FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc curl \
    && rm -rf /var/cache/apk/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Copy Alembic configuration and migrations
COPY alembic.ini .
COPY ./alembic ./alembic

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 8000

# Health check
# HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM python:3.11-alpine 

WORKDIR /app

# Install curl for health checks
RUN apk update && apk add --no-cache \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 5000

# Run the application
CMD [ \
  "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload", \
  "--reload-dir", "/app/app", \
  "--reload-dir", "/shared-ui/static/css/", \
  "--reload-dir", "/shared-ui/static/js/", \
  "--reload-dir", "/shared-ui/static/images/", \
  "--reload-dir", "/shared-ui/templates/components/", \
  "--reload-dir", "/shared-ui/templates/layouts/", \
  "--reload-include", "*.css", \
  "--reload-include", "*.js", \
  "--reload-include", "*.html" \
  ]
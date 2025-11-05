# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

RUN apk add --no-cache cronie

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html
# COPY --from=builder /app/fecrontab /etc/crontabs/root
# COPY --from=builder /app/register_service.sh /register_service.sh
RUN touch /register_service.sh

# Ensure the cron job file has correct permissions
RUN chmod 0600 /etc/crontabs/root

# Create a custom entrypoint script to start both Nginx and cron
RUN chmod +x /register_service.sh

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/dashboard/ || exit 1

EXPOSE 80

# Set the custom entrypoint

CMD ["nginx", "-g", "daemon off;"]

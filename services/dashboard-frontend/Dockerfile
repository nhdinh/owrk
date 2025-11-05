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
FROM nginx:latest

RUN apt-get update && apt-get install -y \
    cron dos2unix && \
    rm -rf /var/lib/apt/lists/*

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create entrypoint wrapper script for modifying the registration script
# and run cron alongside nginx
RUN cat > /nginx-entrypoint-wrapper.sh <<EOF
#!/usr/bin/sh

cat /rs_template > /register_service.sh
sed -i "s#__HOST_NAME__#"\${HOST_NAME}"#g" /register_service.sh
sed -i "s#__HOST_PORT__#"\${HOST_PORT}"#g" /register_service.sh
sed -i "s#__HEALTH_ENDPOINT__#"\${HEALTH_ENDPOINT}"#g" /register_service.sh

dos2unix /register_service.sh
chmod +x /register_service.sh

/register_service.sh

cron && /docker-entrypoint.sh "\$@"
EOF

RUN dos2unix /nginx-entrypoint-wrapper.sh
RUN chmod +x /nginx-entrypoint-wrapper.sh

# create crontab file to run the registration script every 10 minutes
RUN echo "*/10 * * * * /register_service.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/fe-crontab && \
    chmod 0600 /etc/cron.d/fe-crontab && \
    crontab /etc/cron.d/fe-crontab

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/dashboard/ || exit 1

EXPOSE 80

# Set the custom entrypoint
ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

CMD ["nginx", "-g", "daemon off;"]

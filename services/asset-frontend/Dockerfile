FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:latest

RUN apt-get update && apt-get install -y \
    cron dos2unix && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/dist /usr/share/nginx/html
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

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Set the custom entrypoint
ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

CMD ["nginx", "-g", "daemon off;"]

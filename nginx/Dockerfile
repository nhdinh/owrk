FROM nginx:latest

RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

# Create temp file for entrypoint wrapper
RUN echo '#!/bin/sh \
    crond -l 8 &; \
    exec docker-entrypoint.sh "'\$@'"' > /nginx-entrypoint-wrapper.sh && \
    chmod +x /nginx-entrypoint-wrapper.sh

RUN echo "*/1 * * * * /register_service.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/fe-crontab && \
    chmod 0600 /etc/cron.d/fe-crontab && \
    crontab /etc/cron.d/fe-crontab

RUN echo "#!/bin/bash \
    curl -X POST http://service-registry:3000/register \
    -H \"Content-Type: application/json\" \
    -d '{ \
    \"name\": \"'${HOST_NAME}'\", \
    \"hostname\": \"'${HOST_NAME}'\", \
    \"port\": '${HOST_PORT}', \
    \"health_endpoint\": \"'${HEALTH_ENDPOINT}'\" \
    }'" > /register_service.sh && \
    chmod +x /register_service.sh

# ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

# Define your Nginx CMD (e.g., to run Nginx in the foreground)
# CMD ["crond", "-f", "&", "nginx", "-g", "daemon off;"]
CMD ["nginx", "-g", "daemon off;"]
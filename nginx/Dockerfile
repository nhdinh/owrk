FROM nginx:latest

RUN apt-get update && apt-get install -y \
    cron dos2unix && \
    rm -rf /var/lib/apt/lists/*

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

ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

# Define your Nginx CMD (e.g., to run Nginx in the foreground)
# CMD ["crond", "-f", "&", "nginx", "-g", "daemon off;"]
CMD ["nginx", "-g", "daemon off;"]
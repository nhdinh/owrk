#!/bin/sh

cat /rs_template > /register_service.sh
sed -i "s#__HOST_NAME__#"${HOST_NAME}"#g" /register_service.sh
sed -i "s#__HOST_PORT__#"${HOST_PORT}"#g" /register_service.sh
sed -i "s#__HEALTH_ENDPOINT__#"${HEALTH_ENDPOINT}"#g" /register_service.sh

dos2unix /register_service.sh
chmod +x /register_service.sh

/register_service.sh && echo

# cron && /docker-entrypoint.sh "\$@"
/docker-entrypoint.sh "$@"
#!/bin/sh

curl -X POST http://service-registry:3000/register \
     -H "Content-Type: application/json" \
     -d '{
           "name": "'${HOST_NAME}'",
           "hostname": "'${HOST_NAME}'",
           "port": '${HOST_PORT}',
           "health_endpoint": "'${HEALTH_ENDPOINT}'"
         }'
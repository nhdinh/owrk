#!/usr/bin/sh

ADDRESS=$(hostname -i)
    
curl -X POST http://service-registry:3000/register \
    -H "Content-Type: application/json" \
    -d '{
        "name": "__HOST_NAME__",
        "hostname": "__HOST_NAME__",
        "port": __HOST_PORT__,
        "address": "'"$ADDRESS"'",
        "health_endpoint": "__HEALTH_ENDPOINT__"
    }'

#!/bin/bash
    
# Start cron in the background
crond -l 8 &

# Execute the original Nginx entrypoint
exec /docker-entrypoint.sh "$@"
FROM nginx:latest

RUN apt-get update && apt-get install -y \
    dos2unix && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

# Define your Nginx CMD (e.g., to run Nginx in the foreground)
# CMD ["crond", "-f", "&", "nginx", "-g", "daemon off;"]
CMD ["nginx", "-g", "daemon off;"]
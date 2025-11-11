FROM nginx:alpine

RUN apk update && apk add --no-cache dos2unix \
    && rm -rf /var/cache/apk/*

ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

# Define your Nginx CMD (e.g., to run Nginx in the foreground)
CMD ["nginx", "-g", "daemon off;"]
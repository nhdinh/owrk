FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine

RUN apk update && apk add --no-cache dos2unix \
    && rm -rf /var/cache/apk/*

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Set the custom entrypoint
ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

CMD ["nginx", "-g", "daemon off;"]

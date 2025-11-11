# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use install instead of ci since we don't have package-lock.json)
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

RUN apk update && apk add --no-cache dos2unix \
  && rm -rf /var/cache/apk/*

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Set the custom entrypoint
ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

CMD ["nginx", "-g", "daemon off;"]

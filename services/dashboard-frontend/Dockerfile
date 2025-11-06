# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:latest

RUN apt-get update && apt-get install -y \
    dos2unix && \
    rm -rf /var/lib/apt/lists/*

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost/dashboard/ || exit 1

EXPOSE 80

# Set the custom entrypoint
ENTRYPOINT [ "/nginx-entrypoint-wrapper.sh" ]

CMD ["nginx", "-g", "daemon off;"]

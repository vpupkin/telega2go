# Frontend Dockerfile
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with legacy peer deps to fix compatibility issues
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Set environment variables
ENV REACT_APP_BACKEND_URL=http://localhost:5572
ENV REACT_APP_OTP_GATEWAY_URL=http://localhost:5571

# Fix dependency issues and build the application
RUN npm install ajv@^8.0.0 --save-dev --legacy-peer-deps
RUN npm install date-fns@^3.6.0 --save --legacy-peer-deps
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

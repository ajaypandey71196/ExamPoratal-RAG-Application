# Stage 1: Build the frontend
FROM node:18-alpine as builder

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* ./
#RUN npm ci --prefer-offline --no-audit
# Use npm ci for clean install and better caching
RUN --mount=type=cache,target=/root/.npm npm ci --prefer-offline --no-audit

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve the frontend with a lightweight web server
FROM nginx:alpine as runner

# Copy only the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 3000 (or 80 if Nginx default)
EXPOSE 3000

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

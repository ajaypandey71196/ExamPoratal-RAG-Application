# Stage 1: Build the frontend
FROM node:18-alpine as builder

WORKDIR /app

# Copy dependency files
COPY package.json package-lock.json* yarn.lock* ./

# If package-lock.json exists, use npm ci, otherwise use npm install
RUN if [ -f package-lock.json ]; then \
    npm ci --prefer-offline --no-audit; \
    else \
    npm install; \
    fi

# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: Serve the frontend
FROM nginx:alpine as runner

# Copy built assets to Nginx html folder
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
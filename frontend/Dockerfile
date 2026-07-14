# Stage 1: Build the frontend
FROM node:18-alpine as builder

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* ./
RUN npm ci --prefer-offline --no-audit

COPY . .
RUN npm run build

# Stage 2: Serve the frontend with a lightweight web server
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]

# syntax=docker/dockerfile:1

# --- Build the static bundle -------------------------------------------------
FROM node:22-alpine AS builder

WORKDIR /app

# Install dependencies first so the layer is cached across source-only changes.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# --- Serve via nginx, proxying /api to the backend --------------------------
FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

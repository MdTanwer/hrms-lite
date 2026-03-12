# Production frontend: build then nginx (pinned bases for reproducibility)
FROM node:20-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package.json package-lock.json* ./
RUN npm ci

ENV NODE_ENV=production

COPY . .
RUN npm run build

# Final stage: minimal nginx
FROM nginx:1.25-alpine

# Remove default config
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /app/dist /usr/share/nginx/html

# Read-only where possible (nginx needs write for cache/pid; optional)
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O- http://localhost:80/ | head -c 1 > /dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]

FROM node:20-alpine AS base

WORKDIR /app

FROM base AS deps

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

FROM base AS builder

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./

RUN npm run build

FROM base AS runner

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 viteuser

USER viteuser

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

EXPOSE 5173

CMD ["npx", "vite", "preview", "--port", "5173", "--host"]
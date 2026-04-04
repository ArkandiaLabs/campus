FROM node:20-alpine AS deps

WORKDIR /app

RUN corepack enable pnpm

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:20-alpine AS builder

WORKDIR /app

RUN corepack enable pnpm

ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_API_URL

COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN pnpm build

FROM node:20-alpine AS runtime

WORKDIR /app

RUN corepack enable pnpm

ENV NODE_ENV=production

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]

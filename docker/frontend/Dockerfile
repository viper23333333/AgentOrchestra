# ============================================================================
# AgentOrchestra Frontend Dockerfile
# Multi-stage build for Next.js 14 application with pnpm
# ============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Dependencies - Install node modules
# ---------------------------------------------------------------------------
FROM node:20-alpine AS deps

RUN apk add --no-cache libc6-compat

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy package files first for dependency caching
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# Copy public assets (needed for build)
COPY frontend/public ./public

# Install dependencies (frozen lockfile in CI, fallback otherwise)
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm install --frozen-lockfile; \
    else \
        pnpm install; \
    fi

# ---------------------------------------------------------------------------
# Stage 2: Builder - Build the Next.js application
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

RUN apk add --no-cache libc6-compat

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@latest --activate

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source code
COPY frontend/ .

# Set build-time environment variables
ARG NEXT_PUBLIC_API_URL=http://localhost:80/api
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build the application
RUN pnpm build

# ---------------------------------------------------------------------------
# Stage 3: Runtime - Minimal production image
# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

LABEL maintainer="AgentOrchestra Team"
LABEL description="AgentOrchestra Frontend - Multi-Agent Collaboration System UI"
LABEL version="1.0.0"

# Security: Run as non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

WORKDIR /app

# Set environment to production
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# Copy only the necessary build artifacts
COPY --from=builder /app/public ./public

# Set correct permissions for Next.js standalone output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose the application port
EXPOSE 3000

# Set the hostname
ENV HOSTNAME="0.0.0.0" \
    PORT=3000

# Health check - verify the frontend is responsive
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start the Next.js server
CMD ["node", "server.js"]

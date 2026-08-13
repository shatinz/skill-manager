---
id: devops-cloud-serverless.containerization.docker-multi-stage-distroless
name: docker-multi-stage-distroless
title: Docker Multi-Stage Builds with Distroless & Security Hardening
category: devops-cloud-serverless
subcategory: containerization
version: 1.4.0
tags:
- docker
- containers
- distroless
- security
- multi-stage
- cve
- devops
trust_rating: 0.99
estimated_tokens: 1600
description: Construct minimal, secure, vulnerability-free container images using
  multi-stage Dockerfiles, Google Distroless minimal runtimes, non-root users, and
  layer caching optimization.
trigger_patterns:
- docker multi stage distroless
- minimize docker container size cve
- dockerfile non-root security hardening
- docker layer caching best practices
---

# Docker Multi-Stage Builds with Distroless & Security Hardening

## Objective
Eliminate CVE attack vectors, minimize image transfer sizes (<50MB), and enforce non-root security policies by constructing optimized multi-stage Docker builds targeting Distroless runtimes.

## Hardened Multi-Stage Dockerfile (`Dockerfile`)
```dockerfile
# Stage 1: Build Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# Stage 2: Build Application
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Minimal Distroless Production Runner
FROM gcr.io/distroless/nodejs20-debian12:nonroot AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Copy minimal runtime artifacts
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./package.json

USER nonroot:nonroot
EXPOSE 3000

CMD ["dist/index.js"]
```

## Anti-Patterns
- ❌ Running containers as root (`USER 0`).
- ❌ Retaining build tools (compilers, git, devDependencies) in the final runtime container image.

---
id: devops-cloud.ci-cd.docker-multi-stage-build
name: docker-multi-stage-build
title: Production Docker Multi-Stage Optimization & Distroless
category: devops-cloud
subcategory: ci-cd
version: 1.3.0
tags:
- docker
- container
- multi-stage
- distroless
- security
- devops
trust_rating: 0.98
estimated_tokens: 1350
description: Author minimal, secure, and reproducible Docker images using multi-stage
  builds, non-root users, unprivileged distroless base images, and `.dockerignore`.
trigger_patterns:
- optimize dockerfile
- docker multi stage build
- distroless docker image
- secure docker container non-root
---

# Production Docker Multi-Stage Optimization & Distroless

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final Minimal Runtime
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN ["/usr/bin/pip", "install", "--no-index", "--find-links=/wheels", "-r", "requirements.txt"]
COPY --chown=nonroot:nonroot . .
USER nonroot
ENTRYPOINT ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

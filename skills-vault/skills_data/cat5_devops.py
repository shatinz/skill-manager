"""
Category 5: DevOps, Cloud & Serverless (7 Skills)
"""

DEVOPS_CLOUD_SKILLS = [
    {
        "id": "devops-cloud-serverless.containerization.docker-multi-stage-distroless",
        "name": "docker-multi-stage-distroless",
        "title": "Docker Multi-Stage Builds with Distroless & Security Hardening",
        "category": "devops-cloud-serverless",
        "subcategory": "containerization",
        "version": "1.4.0",
        "tags": ["docker", "containers", "distroless", "security", "multi-stage", "cve", "devops"],
        "trust_rating": 0.99,
        "estimated_tokens": 1600,
        "description": "Construct minimal, secure, vulnerability-free container images using multi-stage Dockerfiles, Google Distroless minimal runtimes, non-root users, and layer caching optimization.",
        "trigger_patterns": [
            "docker multi stage distroless",
            "minimize docker container size cve",
            "dockerfile non-root security hardening",
            "docker layer caching best practices"
        ],
        "content": """# Docker Multi-Stage Builds with Distroless & Security Hardening

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
"""
    },

    {
        "id": "devops-cloud-serverless.ci-cd.github-actions-matrix-ci",
        "name": "github-actions-matrix-ci",
        "title": "GitHub Actions Matrix CI/CD Workflows & Dependency Caching",
        "category": "devops-cloud-serverless",
        "subcategory": "ci-cd",
        "version": "1.3.0",
        "tags": ["github-actions", "ci-cd", "matrix-builds", "caching", "devops", "automation"],
        "trust_rating": 0.98,
        "estimated_tokens": 1550,
        "description": "Construct high-speed, parallel matrix CI/CD workflows in GitHub Actions with deterministic dependency caching, concurrency controls, and OIDC cloud authentication.",
        "trigger_patterns": [
            "github actions matrix build workflow",
            "github actions cache node_modules pip",
            "github actions concurrency cancel in progress",
            "github actions oidc aws deploy"
        ],
        "content": """# GitHub Actions Matrix CI/CD Workflows & Dependency Caching

## Objective
Accelerate continuous integration pipelines using parallel OS/version matrix builds, aggressive cache strategies, and secure OIDC deployments without long-lived access tokens.

## Production CI Workflow (`.github/workflows/ci.yml`)
```yaml
name: Continuous Integration

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest]
        python-version: ['3.11', '3.12']
        node-version: ['20', '22']

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Setup Node ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          npm ci

      - name: Run Test Suite
        run: |
          pytest --cov=app --cov-report=xml
          npm test
```

## Anti-Patterns
- ❌ Missing concurrency cancellation, wasting runner minutes on stale PR commits.
- ❌ Hardcoding plain AWS credentials in GitHub Secrets instead of utilizing OIDC role assumption.
"""
    },

    {
        "id": "devops-cloud-serverless.iac-cloud.terraform-aws-modules",
        "name": "terraform-aws-modules",
        "title": "Terraform AWS Modular Infrastructure as Code (IaC)",
        "category": "devops-cloud-serverless",
        "subcategory": "iac-cloud",
        "version": "1.3.0",
        "tags": ["terraform", "aws", "iac", "modules", "vpc", "ecs", "s3", "state-locking"],
        "trust_rating": 0.97,
        "estimated_tokens": 1600,
        "description": "Structure clean, reusable Terraform modules for AWS with S3 remote state backends, DynamoDB state locking, least-privilege security groups, and automated plan verifications.",
        "trigger_patterns": [
            "terraform aws module architecture",
            "terraform s3 backend dynamodb state lock",
            "terraform vpc security group module",
            "terraform plan automated validation"
        ],
        "content": """# Terraform AWS Modular Infrastructure as Code (IaC)

## Objective
Author modular, maintainable, and secure Terraform configurations for AWS cloud infrastructure with remote state locking and strict variable validation.

## Remote Backend & Modular VPC (`main.tf`)
```hcl
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "production-terraform-state-vault"
    key            = "core/infrastructure.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "${var.environment}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "production"
}
```

## Anti-Patterns
- ❌ Storing `.tfstate` files in local git repositories.
- ❌ Authoring wide-open ingress rules (`0.0.0.0/0`) on internal database ports.
"""
    },

    {
        "id": "devops-cloud-serverless.edge-serverless.cloudflare-workers-kv-d1",
        "name": "cloudflare-workers-kv-d1",
        "title": "Cloudflare Workers, KV, D1 SQL & Durable Objects",
        "category": "devops-cloud-serverless",
        "subcategory": "edge-serverless",
        "version": "1.3.0",
        "tags": ["cloudflare-workers", "kv", "d1", "durable-objects", "edge", "wrangler", "typescript"],
        "trust_rating": 0.98,
        "estimated_tokens": 1600,
        "description": "Develop and deploy globally distributed, low-latency edge services using Cloudflare Workers, KV caching, D1 relational SQLite storage, and stateful Durable Objects.",
        "trigger_patterns": [
            "cloudflare workers d1 database setup",
            "cloudflare workers kv binding wrangler",
            "cloudflare durable objects websocket",
            "deploy edge service cloudflare workers"
        ],
        "content": """# Cloudflare Workers, KV, D1 SQL & Durable Objects

## Objective
Build low-latency, globally replicated edge applications with zero server provisioning using Cloudflare Workers, D1 distributed SQL, and persistent Durable Objects.

## Configuration & Edge Worker (`wrangler.toml` & `worker.ts`)
```toml
name = "edge-api-gateway"
main = "src/index.ts"
compatibility_date = "2025-01-01"

[[d1_databases]]
binding = "DB"
database_name = "production-d1"
database_id = "xxxx-xxxx-xxxx"

[[kv_namespaces]]
binding = "CACHE"
id = "yyyy-yyyy-yyyy"
```

```typescript
export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/items') {
      # Check edge KV cache
      const cached = await env.CACHE.get('items_list');
      if (cached) {
        return new Response(cached, { headers: { 'Content-Type': 'application/json', 'X-Cache': 'HIT' } });
      }

      # Query D1 Distributed SQLite
      const { results } = await env.DB.prepare('SELECT id, name, price FROM items ORDER BY price ASC LIMIT 50').all();
      const body = JSON.stringify(results);

      await env.CACHE.put('items_list', body, { expirationTtl: 300 });
      return new Response(body, { headers: { 'Content-Type': 'application/json', 'X-Cache': 'MISS' } });
    }

    return new Response('Not Found', { status: 404 });
  },
};
```

## Anti-Patterns
- ❌ Performing unindexed heavy joins in D1 edge SQLite databases.
"""
    },

    {
        "id": "devops-cloud-serverless.deployment-gitops.vercel-zero-downtime-deploy",
        "name": "vercel-zero-downtime-deploy",
        "title": "Vercel Zero-Downtime Deployments, Preview GitOps & Edge Middleware",
        "category": "devops-cloud-serverless",
        "subcategory": "deployment-gitops",
        "version": "1.2.0",
        "tags": ["vercel", "gitops", "zero-downtime", "edge-middleware", "preview-environments", "nextjs"],
        "trust_rating": 0.96,
        "estimated_tokens": 1450,
        "description": "Configure zero-downtime production rollouts, GitOps branch preview environments, security headers, and edge middleware routing using Vercel CLI and configuration.",
        "trigger_patterns": [
            "vercel zero downtime deployment",
            "vercel preview branch gitops",
            "vercel.json security headers rewrite",
            "vercel edge middleware routing"
        ],
        "content": """# Vercel Zero-Downtime Deployments & Preview GitOps

## Objective
Establish deterministic GitOps pipelines with instant atomic rollbacks, isolated preview environments per PR, and custom edge routing via `vercel.json`.

## Vercel Security & Routing Configuration (`vercel.json`)
```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()" }
      ]
    }
  ]
}
```

## Anti-Patterns
- ❌ Pushing direct untracked manual CLI overrides to production without Git PR audit trails.
"""
    },

    {
        "id": "devops-cloud-serverless.orchestration.kubernetes-helm-microservice",
        "name": "kubernetes-helm-microservice",
        "title": "Kubernetes & Helm Chart Microservice Deployment Specs",
        "category": "devops-cloud-serverless",
        "subcategory": "orchestration",
        "version": "1.3.0",
        "tags": ["kubernetes", "k8s", "helm", "microservices", "ingress", "hpa", "cloud-native"],
        "trust_rating": 0.98,
        "estimated_tokens": 1650,
        "description": "Author production Kubernetes manifests and parameterized Helm v3 charts with Horizontal Pod Autoscaling (HPA), Liveness/Readiness probes, and PodDisruptionBudgets.",
        "trigger_patterns": [
            "kubernetes helm chart microservice",
            "k8s hpa autoscaling deployment",
            "kubernetes readiness liveness probes",
            "helm values template deployment"
        ],
        "content": """# Kubernetes & Helm Chart Microservice Deployment Specs

## Objective
Author highly available, cloud-native Kubernetes workloads using parameterized Helm v3 templates with graceful zero-downtime rolling updates and resource limits.

## Production Helm Template (`templates/deployment.yaml`)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-service
  labels:
    app.kubernetes.io/name: {{ .Chart.Name }}
    app.kubernetes.io/instance: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: app
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
```

## Anti-Patterns
- ❌ Omitting container resource requests/limits, allowing rogue pods to exhaust worker node memory (causing node OOM-Kills).
"""
    },

    {
        "id": "devops-cloud-serverless.observability.prometheus-grafana-telemetry",
        "name": "prometheus-grafana-telemetry",
        "title": "Prometheus Metrics, Grafana Dashboards & OpenTelemetry",
        "category": "devops-cloud-serverless",
        "subcategory": "observability",
        "version": "1.3.0",
        "tags": ["prometheus", "grafana", "opentelemetry", "metrics", "alerts", "telemetry", "tracing"],
        "trust_rating": 0.97,
        "estimated_tokens": 1600,
        "description": "Implement the RED method (Rate, Errors, Duration) metrics with Prometheus, export OpenTelemetry distributed traces, and define actionable alert rules.",
        "trigger_patterns": [
            "prometheus metrics promql alerts",
            "opentelemetry distributed tracing python",
            "grafana red method dashboard",
            "prometheus alertmanager rules"
        ],
        "content": """# Prometheus Metrics, Grafana Dashboards & OpenTelemetry

## Objective
Establish full-stack observability using Prometheus RED metrics, OpenTelemetry distributed tracing spans, and high-signal alert rules without noise fatigue.

## OpenTelemetry Instrumentation (`instrumentation.py`)
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram

# Prometheus RED Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total requests", ["method", "endpoint", "status"])
REQUEST_DURATION = Histogram("http_request_duration_seconds", "Request latency", ["endpoint"])

# OpenTelemetry Tracer Setup
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("agent-core")

def execute_instrumented_task(task_name: str):
    with tracer.start_as_current_span(task_name) as span:
        span.set_attribute("task.name", task_name)
        # Business logic execution
        return "Task Completed"
```

## Anti-Patterns
- ❌ High-cardinality label dimensions in Prometheus (e.g. adding `user_id` or `uuid` as a metric label).
"""
    }
]

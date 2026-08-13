# 🏛️ Public Agentic Skill Vault

> A community-driven, living ecosystem of reusable agentic capabilities, instructions, and workflows for autonomous AI agents.

## 📊 Overview
- **Total Skills**: 24
- **Categories**: 6
- **Subcategories**: 14

## 🗂️ Categories & Taxonomy

### 📁 `coding`
- **`api-design`** (3 skills)
  - [`fastapi-rest-craft`](skills/coding/api-design/fastapi-rest-craft/SKILL.md)
  - [`graphql-schema-design`](skills/coding/api-design/graphql-schema-design/SKILL.md)
  - [`grpc-protobuf-specs`](skills/coding/api-design/grpc-protobuf-specs/SKILL.md)
- **`database-architecture`** (2 skills)
  - [`postgres-query-tuning`](skills/coding/database-architecture/postgres-query-tuning/SKILL.md)
  - [`prisma-orm-patterns`](skills/coding/database-architecture/prisma-orm-patterns/SKILL.md)
- **`frontend-engineering`** (2 skills)
  - [`react-performance-audit`](skills/coding/frontend-engineering/react-performance-audit/SKILL.md)
  - [`tailwind-design-system`](skills/coding/frontend-engineering/tailwind-design-system/SKILL.md)
- **`refactoring-clean-code`** (2 skills)
  - [`legacy-code-modernizer`](skills/coding/refactoring-clean-code/legacy-code-modernizer/SKILL.md)
  - [`dry-solid-refactor`](skills/coding/refactoring-clean-code/dry-solid-refactor/SKILL.md)

### 📁 `data-ai-engineering`
- **`data-pipelines`** (1 skills)
  - [`duckdb-fast-analytics`](skills/data-ai-engineering/data-pipelines/duckdb-fast-analytics/SKILL.md)
- **`llm-rag`** (2 skills)
  - [`rag-chunking-hybrid-search`](skills/data-ai-engineering/llm-rag/rag-chunking-hybrid-search/SKILL.md)
  - [`prompt-engineering-distiller`](skills/data-ai-engineering/llm-rag/prompt-engineering-distiller/SKILL.md)

### 📁 `devops-cloud`
- **`ci-cd`** (2 skills)
  - [`github-actions-matrix-ci`](skills/devops-cloud/ci-cd/github-actions-matrix-ci/SKILL.md)
  - [`docker-multi-stage-build`](skills/devops-cloud/ci-cd/docker-multi-stage-build/SKILL.md)
- **`infrastructure-as-code`** (1 skills)
  - [`terraform-aws-modules`](skills/devops-cloud/infrastructure-as-code/terraform-aws-modules/SKILL.md)
- **`observability`** (1 skills)
  - [`prometheus-grafana-telemetry`](skills/devops-cloud/observability/prometheus-grafana-telemetry/SKILL.md)

### 📁 `documentation-communication`
- **`api-docs`** (1 skills)
  - [`openapi-swagger-generator`](skills/documentation-communication/api-docs/openapi-swagger-generator/SKILL.md)
- **`architecture-decision-records`** (1 skills)
  - [`adr-writer-reviewer`](skills/documentation-communication/architecture-decision-records/adr-writer-reviewer/SKILL.md)

### 📁 `security-compliance`
- **`code-hardening`** (2 skills)
  - [`jwt-oauth2-secureshop`](skills/security-compliance/code-hardening/jwt-oauth2-secureshop/SKILL.md)
  - [`input-sanitization-guard`](skills/security-compliance/code-hardening/input-sanitization-guard/SKILL.md)

### 📁 `testing-quality`
- **`security-sast`** (2 skills)
  - [`owasp-top10-scanner`](skills/testing-quality/security-sast/owasp-top10-scanner/SKILL.md)
  - [`secret-leak-detector`](skills/testing-quality/security-sast/secret-leak-detector/SKILL.md)
- **`unit-integration`** (2 skills)
  - [`pytest-mocking-mastery`](skills/testing-quality/unit-integration/pytest-mocking-mastery/SKILL.md)
  - [`playwright-e2e-automation`](skills/testing-quality/unit-integration/playwright-e2e-automation/SKILL.md)

## ⚡ Using with the `askill` CLI

Agents can discover and fetch skills on-demand without cloning the entire repository:

```bash
# Smart search by task intent
askill search "build production rest api with postgres"

# Inject matching skill directly into agent prompt
askill match --task "optimize react re-renders"

# Fetch skill markdown on demand
askill get coding.api-design.fastapi-rest-craft

# Propose an improvement or PR
askill propose --skill coding.api-design.fastapi-rest-craft --file patch.diff --reason "Added Pydantic v2 model_config"
```

## 🤝 Contributing
Every skill is a living document. Propose updates via PR or submit proposals through the `askill propose` CLI.

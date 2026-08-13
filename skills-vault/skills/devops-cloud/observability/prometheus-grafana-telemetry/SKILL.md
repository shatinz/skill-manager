---
id: devops-cloud.observability.prometheus-grafana-telemetry
name: prometheus-grafana-telemetry
title: Prometheus, Grafana & OpenTelemetry Observability Stack
category: devops-cloud
subcategory: observability
version: 1.0.0
tags:
- prometheus
- grafana
- opentelemetry
- metrics
- tracing
- monitoring
trust_rating: 0.91
estimated_tokens: 1300
description: Instrument applications with OpenTelemetry traces, export RED metrics
  (Rate, Errors, Duration) to Prometheus, and design actionable Grafana alert dashboards.
trigger_patterns:
- setup prometheus metrics
- grafana dashboard alerts
- opentelemetry tracing instrumentation
- red metrics monitoring
---

# Prometheus, Grafana & OpenTelemetry Observability Stack

## Metrics Checklist
- **Counter**: Total requests, failed jobs.
- **Histogram**: Latency distributions with exponential bucket sizing.
- **Gauge**: Active database connections, queue depths.

---
id: devops-cloud-serverless.observability.prometheus-grafana-telemetry
name: prometheus-grafana-telemetry
title: Prometheus Metrics, Grafana Dashboards & OpenTelemetry
category: devops-cloud-serverless
subcategory: observability
version: 1.3.0
tags:
- prometheus
- grafana
- opentelemetry
- metrics
- alerts
- telemetry
- tracing
trust_rating: 0.97
estimated_tokens: 1600
description: Implement the RED method (Rate, Errors, Duration) metrics with Prometheus,
  export OpenTelemetry distributed traces, and define actionable alert rules.
trigger_patterns:
- prometheus metrics promql alerts
- opentelemetry distributed tracing python
- grafana red method dashboard
- prometheus alertmanager rules
---

# Prometheus Metrics, Grafana Dashboards & OpenTelemetry

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

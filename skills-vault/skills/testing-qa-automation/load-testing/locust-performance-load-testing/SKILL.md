---
id: testing-qa-automation.load-testing.locust-performance-load-testing
name: locust-performance-load-testing
title: Locust Distributed Load Testing & Latency Benchmarking
category: testing-qa-automation
subcategory: load-testing
version: 1.2.0
tags:
- locust
- load-testing
- performance
- benchmarking
- stress-testing
- python
trust_rating: 0.96
estimated_tokens: 1500
description: Benchmark API throughput, p95/p99 latencies, and concurrency limits using
  Locust Python-as-code distributed load test scenarios.
trigger_patterns:
- locust python load testing setup
- benchmark api p99 latency locust
- distributed load testing locust workers
- locust task weighting user journey
---

# Locust Distributed Load Testing & Latency Benchmarking

## Objective
Simulate thousands of concurrent user journeys in pure Python to uncover system concurrency ceilings, database connection pool exhaustion, and memory leaks.

## Load Scenario Blueprint (`locustfile.py`)
```python
from locust import HttpUser, task, between

class APIStressUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def view_catalog(self):
        self.client.get("/v1/items?limit=20", name="/v1/items")

    @task(1)
    def place_order(self):
        payload = {"sku": "SKU-999", "quantity": 1}
        with self.client.post("/v1/orders", json=payload, name="/v1/orders", catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Failed with status: {response.status_code}")
```

## Anti-Patterns
- ❌ Running high-concurrency load tests from a single machine without distributed worker nodes.

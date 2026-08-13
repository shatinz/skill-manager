---
id: devops-cloud-serverless.orchestration.kubernetes-helm-microservice
name: kubernetes-helm-microservice
title: Kubernetes & Helm Chart Microservice Deployment Specs
category: devops-cloud-serverless
subcategory: orchestration
version: 1.3.0
tags:
- kubernetes
- k8s
- helm
- microservices
- ingress
- hpa
- cloud-native
trust_rating: 0.98
estimated_tokens: 1650
description: Author production Kubernetes manifests and parameterized Helm v3 charts
  with Horizontal Pod Autoscaling (HPA), Liveness/Readiness probes, and PodDisruptionBudgets.
trigger_patterns:
- kubernetes helm chart microservice
- k8s hpa autoscaling deployment
- kubernetes readiness liveness probes
- helm values template deployment
---

# Kubernetes & Helm Chart Microservice Deployment Specs

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

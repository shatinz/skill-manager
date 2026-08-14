---
id: devops-cloud-serverless.gitops-orchestration.kubernetes-helm-gitops-argocd
name: kubernetes-helm-gitops-argocd
title: ArgoCD GitOps, Helm Orchestration & Multi-Cluster Sync
category: devops-cloud-serverless
subcategory: gitops-orchestration
version: 1.3.0
tags:
- argocd
- gitops
- kubernetes
- helm
- kustomize
- multi-cluster
- declarative
trust_rating: 0.98
estimated_tokens: 1750
description: Implement declarative Kubernetes continuous delivery with ArgoCD ApplicationSets,
  Helm chart overlays, automated drift detection, self-healing, and zero-downtime
  progressive rollouts.
trigger_patterns:
- argocd gitops application manifest
- helm values override argocd sync
- argocd applicationset multi cluster
- kubernetes declarative gitops pipeline
---

# ArgoCD GitOps, Helm Orchestration & Multi-Cluster Sync

## Objective
Establish automated, declarative continuous deployment for cloud-native microservices using ArgoCD GitOps pipelines, Helm templating, and automated state synchronization.

## ArgoCD Application Manifest (`argocd/production-app.yaml`)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: core-services-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: 'https://github.com/org/infra-gitops.git'
    targetRevision: HEAD
    path: charts/core-service
    helm:
      valueFiles:
        - ../../environments/production/values.yaml
  destination:
    server: 'https://kubernetes.default.svc'
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ApplyOutOfSyncOnly=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

## Anti-Patterns
- ❌ Manual `kubectl apply` interventions in production clusters (Git repository must always remain the single source of truth).
- ❌ Disabling automated self-healing without an active incident mitigation reason.

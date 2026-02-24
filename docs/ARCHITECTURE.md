# Architecture

## Overview

This platform runs on AWS EKS with a GitOps deployment model. All infrastructure is provisioned via Terraform. Application deployments are managed by ArgoCD, which watches this Git repository and auto-syncs changes to the cluster.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                         │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ apps/    │  │ terraform/   │  │ kubernetes/               │  │
│  │ (source) │  │ (infra)      │  │ (manifests + helm values) │  │
│  └────┬─────┘  └──────┬───────┘  └─────────────┬─────────────┘  │
└───────┼───────────────┼─────────────────────────┼────────────────┘
        │               │                         │
   GitHub Actions    GitHub Actions            ArgoCD (GitOps)
   (Build+Push)     (Plan+Apply)              (Auto-sync)
        │               │                         │
        ▼               ▼                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                                 │
│                                                                    │
│  ┌──────────┐  ┌─────────────────────────────────────────────┐    │
│  │   ECR    │  │              VPC (10.0.0.0/16)              │    │
│  │ (images) │  │                                              │    │
│  └──────────┘  │  ┌─────────────────────────────────────┐    │    │
│                │  │        EKS Cluster                    │    │    │
│                │  │                                       │    │    │
│                │  │  ┌─────────────┐  ┌──────────────┐   │    │    │
│                │  │  │microservices│  │  monitoring   │   │    │    │
│                │  │  │ namespace   │  │  namespace    │   │    │    │
│                │  │  │             │  │               │   │    │    │
│                │  │  │ api-gateway │  │ Prometheus    │   │    │    │
│                │  │  │ order-svc   │  │ Grafana       │   │    │    │
│                │  │  │ notif-svc   │  │ Loki+Promtail │   │    │    │
│                │  │  └─────────────┘  └──────────────┘   │    │    │
│                │  │                                       │    │    │
│                │  │  ┌─────────────┐                     │    │    │
│                │  │  │   argocd    │                     │    │    │
│                │  │  │  namespace  │                     │    │    │
│                │  │  │  ArgoCD     │                     │    │    │
│                │  │  └─────────────┘                     │    │    │
│                │  │                                       │    │    │
│                │  │  Spot Instances (t3.medium x2)        │    │    │
│                │  └───────────────────────────────────────┘    │    │
│                │                                              │    │
│                │  Public Subnets ──── NAT GW ──── Private     │    │
│                │  (ALB)              (single)     Subnets     │    │
│                │                                  (EKS nodes) │    │
│                └──────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Developer pushes code** to GitHub
2. **GitHub Actions CI** runs tests and linting on PRs
3. **On merge to main**, GitHub Actions builds Docker images and pushes to ECR
4. **ArgoCD detects** manifest changes in Git and auto-syncs to the cluster
5. **Prometheus scrapes** /metrics endpoints from all microservices
6. **Grafana dashboards** visualize metrics; Loki aggregates logs
7. **ALB Ingress** routes external traffic to the api-gateway

## Cost Optimization

| Strategy | Savings |
|----------|---------|
| Spot instances for worker nodes | ~60% vs on-demand |
| Single NAT gateway (not per-AZ) | ~$65/mo |
| No persistent storage for Loki (dev) | ~$20/mo |
| In-memory data stores (no RDS/DynamoDB) | ~$50+/mo |
| Tear down when not in use | 100% |

## Security

- Worker nodes in private subnets (no public IPs)
- IRSA (IAM Roles for Service Accounts) enabled
- ECR image scanning on push
- Cluster API audit logging enabled
- Network segmentation via Kubernetes namespaces
- Resource limits on all containers

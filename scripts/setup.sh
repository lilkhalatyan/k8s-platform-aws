#!/bin/bash
set -euo pipefail

echo "=============================================="
echo "  K8s Platform AWS - Full Setup"
echo "=============================================="

# Check prerequisites
echo ""
echo "[1/6] Checking prerequisites..."
for cmd in aws terraform kubectl docker; do
    if ! command -v $cmd &> /dev/null; then
        echo "ERROR: $cmd is not installed. Please install it first."
        exit 1
    fi
done
echo "  All prerequisites found."

# Terraform init and apply
echo ""
echo "[2/6] Provisioning infrastructure with Terraform..."
cd terraform
terraform init
terraform apply -auto-approve
cd ..

# Update kubeconfig
echo ""
echo "[3/6] Updating kubeconfig..."
CLUSTER_NAME=$(cd terraform && terraform output -raw cluster_name)
AWS_REGION=$(cd terraform && terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$AWS_REGION"

# Wait for nodes to be ready
echo ""
echo "[4/6] Waiting for nodes to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Apply ArgoCD app-of-apps
echo ""
echo "[5/6] Deploying ArgoCD app-of-apps..."
kubectl apply -f kubernetes/argocd/app-of-apps.yaml

# Wait for deployments
echo ""
echo "[6/6] Waiting for microservices to be ready..."
kubectl wait --for=condition=Available deployment --all -n microservices --timeout=300s 2>/dev/null || \
    echo "  Microservices namespace not yet created. ArgoCD will sync shortly."

echo ""
echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "  ArgoCD UI:"
echo "    URL:      $(kubectl get svc -n argocd argocd-server -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo 'Pending...')"
echo "    Username: admin"
echo "    Password: $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d)"
echo ""
echo "  Grafana:"
echo "    URL:      $(kubectl get svc -n monitoring kube-prometheus-stack-grafana -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo 'Pending...')"
echo "    Username: admin"
echo "    Password: admin"
echo ""
echo "  Run 'make health-check' to verify all services."
echo "  Run 'make infra-down' to tear down everything."

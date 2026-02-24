#!/bin/bash
set -euo pipefail

echo "=============================================="
echo "  K8s Platform AWS - Teardown"
echo "=============================================="
echo ""
echo "  WARNING: This will destroy ALL infrastructure!"
echo "  This action cannot be undone."
echo ""
read -p "  Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "  Aborted."
    exit 0
fi

echo ""
echo "[1/3] Removing ArgoCD applications..."
kubectl delete application --all -n argocd 2>/dev/null || echo "  No ArgoCD applications found."

echo ""
echo "[2/3] Waiting for resources to be cleaned up..."
sleep 30

echo ""
echo "[3/3] Destroying infrastructure with Terraform..."
cd terraform
terraform destroy -auto-approve
cd ..

echo ""
echo "=============================================="
echo "  Teardown Complete!"
echo "  All resources have been destroyed."
echo "=============================================="

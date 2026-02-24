output "argocd_url" {
  description = "ArgoCD server URL (retrieve after deployment via kubectl)"
  value       = "Run: kubectl get svc -n argocd argocd-server -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'"
}

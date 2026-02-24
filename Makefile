.PHONY: help infra-up infra-down infra-plan build push test lint health-check argocd-password

TERRAFORM_DIR = terraform
APPS = api-gateway order-service notification-service
AWS_REGION ?= us-east-1
AWS_ACCOUNT_ID ?= $(shell aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY = $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
IMAGE_TAG ?= $(shell git rev-parse --short HEAD)

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

## Infrastructure
infra-up: ## Deploy all infrastructure (Terraform)
	cd $(TERRAFORM_DIR) && terraform init && terraform apply

infra-down: ## Destroy all infrastructure
	cd $(TERRAFORM_DIR) && terraform destroy

infra-plan: ## Preview infrastructure changes
	cd $(TERRAFORM_DIR) && terraform init && terraform plan

## Docker
build: ## Build all Docker images
	@for app in $(APPS); do \
		echo "Building $$app..."; \
		docker build -t $$app:$(IMAGE_TAG) -t $$app:latest apps/$$app/; \
	done

push: ## Push all Docker images to ECR
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(ECR_REGISTRY)
	@for app in $(APPS); do \
		echo "Pushing $$app..."; \
		docker tag $$app:$(IMAGE_TAG) $(ECR_REGISTRY)/$$app:$(IMAGE_TAG); \
		docker tag $$app:latest $(ECR_REGISTRY)/$$app:latest; \
		docker push $(ECR_REGISTRY)/$$app:$(IMAGE_TAG); \
		docker push $(ECR_REGISTRY)/$$app:latest; \
	done

## Testing
test: ## Run all Python tests
	@for app in $(APPS); do \
		echo "Testing $$app..."; \
		cd apps/$$app && python -m pytest tests/ -v && cd ../..; \
	done

lint: ## Run all linters
	cd $(TERRAFORM_DIR) && terraform fmt -check -recursive
	black --check apps/
	pylint apps/*/app.py

## Operations
health-check: ## Check health of all services
	python scripts/health_checker.py

cluster-report: ## Generate cluster status report
	python scripts/cluster_report.py

argocd-password: ## Get ArgoCD admin password
	kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

## Setup
setup: ## Full cluster bootstrap
	bash scripts/setup.sh

teardown: ## Full cluster teardown
	bash scripts/teardown.sh

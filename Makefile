# Variables
CLUSTER_PROVIDER ?= k3d
CLUSTER_NAME ?= nexus-platform
AWS_CREDS ?= ./aws-creds.ini

.PHONY: help check-deps create-cluster delete-cluster install-argocd bootstrap configure-aws up setup clean destroy

# Default target: show help
help:
	@echo "GitOps IDP Blueprint Makefile"
	@echo "Usage: make <target> [CLUSTER_PROVIDER=k3d|minikube|kind|existing] [CLUSTER_NAME=nexus-platform]"
	@echo ""
	@echo "Targets:"
	@echo "  up / setup      - Full setup: check deps, create cluster, install ArgoCD, bootstrap platform, configure AWS"
	@echo "  create-cluster  - Provision Kubernetes cluster using specified provider"
	@echo "  delete-cluster  - Delete the provisioned Kubernetes cluster"
	@echo "  install-argocd  - Install ArgoCD via Helm"
	@echo "  bootstrap       - Bootstrap platform applications using ArgoCD"
	@echo "  configure-aws   - Create AWS credentials secret in crossplane-system namespace"
	@echo "  clean           - Remove deployed components (keep cluster)"
	@echo "  destroy         - Full teardown of components and cluster"
	@echo "  check-deps      - Validate required command-line utilities"

# Conditional commands based on CLUSTER_PROVIDER
ifeq ($(CLUSTER_PROVIDER),k3d)
CREATE_CLUSTER_CMD = k3d cluster create $(CLUSTER_NAME) \
	--k3s-arg "--disable=traefik,servicelb@server:*" \
	--k3s-arg "--flannel-backend=none@server:*" \
	--k3s-arg "--disable-network-policy@server:*" \
	--k3s-arg "--disable-kube-proxy@server:*" \
	-p "80:80@loadbalancer" -p "443:443@loadbalancer" && \
	echo "Mounting bpffs on k3d nodes..." && \
	for node in $$(docker ps -f "name=k3d-$(CLUSTER_NAME)" --format "{{.Names}}"); do \
		docker exec $$node mount bpffs /sys/fs/bpf -t bpf || true; \
		docker exec $$node mount --make-shared /sys/fs/bpf || true; \
	done
DELETE_CLUSTER_CMD = k3d cluster delete $(CLUSTER_NAME)
else ifeq ($(CLUSTER_PROVIDER),minikube)
CREATE_CLUSTER_CMD = minikube start --profile $(CLUSTER_NAME) && minikube addons enable ingress --profile $(CLUSTER_NAME)
DELETE_CLUSTER_CMD = minikube delete --profile $(CLUSTER_NAME)
else ifeq ($(CLUSTER_PROVIDER),kind)
CREATE_CLUSTER_CMD = printf 'apiVersion: kind.x-k8s.io/v1alpha4\nkind: Cluster\nnodes:\n- role: control-plane\n  extraPortMappings:\n  - containerPort: 80\n    hostPort: 80\n    listenAddress: "127.0.0.1"\n    protocol: TCP\n  - containerPort: 443\n    hostPort: 443\n    listenAddress: "127.0.0.1"\n    protocol: TCP\n' | kind create cluster --name $(CLUSTER_NAME) --config=-
DELETE_CLUSTER_CMD = kind delete cluster --name $(CLUSTER_NAME)
else
CREATE_CLUSTER_CMD = @echo "Using existing Kubernetes cluster (context: \$$(kubectl config current-context))"
DELETE_CLUSTER_CMD = @echo "Skipping cluster deletion for existing/external cluster"
endif

check-deps:
	@echo "Checking dependencies..."
	@which kubectl > /dev/null || (echo "Error: kubectl is not installed" && exit 1)
	@which helm > /dev/null || (echo "Error: helm is not installed" && exit 1)
ifeq ($(CLUSTER_PROVIDER),k3d)
	@which k3d > /dev/null || (echo "Error: k3d is not installed" && exit 1)
else ifeq ($(CLUSTER_PROVIDER),minikube)
	@which minikube > /dev/null || (echo "Error: minikube is not installed" && exit 1)
else ifeq ($(CLUSTER_PROVIDER),kind)
	@which kind > /dev/null || (echo "Error: kind is not installed" && exit 1)
endif
	@echo "All dependencies satisfied!"

create-cluster: check-deps
	@echo "Creating cluster using $(CLUSTER_PROVIDER) provider..."
	$(CREATE_CLUSTER_CMD)
ifeq ($(CLUSTER_PROVIDER),minikube)
	@echo "============================================================"
	@echo "NOTE: When using minikube on macOS, you may need to run:"
	@echo "      sudo minikube tunnel --profile $(CLUSTER_NAME)"
	@echo "      in a separate terminal to expose services on localhost."
	@echo "============================================================"
endif

delete-cluster:
	@echo "Deleting cluster..."
	$(DELETE_CLUSTER_CMD)

install-cilium:
ifeq ($(CLUSTER_PROVIDER),k3d)
	@echo "Adding Cilium Helm repository..."
	helm repo add cilium https://helm.cilium.io/
	helm repo update
	@echo "Installing Cilium CNI..."
	helm upgrade --install cilium cilium/cilium \
		--version 1.19.4 \
		--namespace kube-system \
		--create-namespace \
		--set kubeProxyReplacement=true \
		--set k8sServiceHost=k3d-$(CLUSTER_NAME)-server-0 \
		--set k8sServicePort=6443 \
		--set bpf.masquerade=false \
		--set l2announcements.enabled=true \
		--set operator.replicas=1 \
		--set ingressController.enabled=true \
		--set ingressController.default=true \
		--set ingressController.loadbalancerMode=shared
else
	@echo "Skipping Cilium installation for $(CLUSTER_PROVIDER)"
endif

install-argocd:
	@echo "Adding ArgoCD Helm repository..."
	helm repo add argo https://argoproj.github.io/argo-helm
	helm repo update
	@echo "Installing/Upgrading ArgoCD..."
	helm upgrade --install argocd argo/argo-cd \
		--namespace argocd \
		--reuse-values \
		--set server.extraArgs="{--insecure}" \
		--create-namespace

bootstrap:
	@echo "Bootstrapping platform..."
	kubectl apply -f bootstrap.yaml

configure-aws:
	@echo "Ensuring crossplane-system namespace exists..."
	kubectl create namespace crossplane-system --dry-run=client -o yaml | kubectl apply -f -
	@echo "Creating/updating AWS credentials secret..."
	kubectl create secret generic aws-creds -n crossplane-system --from-file=creds=$(AWS_CREDS) --dry-run=client -o yaml | kubectl apply -f -

up setup: create-cluster install-cilium install-argocd bootstrap configure-aws
	@echo "Platform setup completed successfully!"

clean:
	@echo "Cleaning up deployed components..."
	kubectl delete -f bootstrap.yaml --ignore-not-found=true
	helm uninstall argocd -n argocd || true
	kubectl delete namespace argocd --ignore-not-found=true
	kubectl delete secret aws-creds -n crossplane-system --ignore-not-found=true

destroy: clean delete-cluster
	@echo "Platform completely destroyed!"

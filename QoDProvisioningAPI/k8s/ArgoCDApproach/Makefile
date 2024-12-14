# Variables
HELM_CHART_DIR = chart
HELM_CHART_NAME = camaraaas-qod-provisioning-api-chart
REPOSITORY_HOST = atnog-harbor.av.it.pt/camaraaas

KUBECONFIG ?= /etc/rancher/k3s/k3s.yaml 
NAMESPACE = itav-slice-manager-client


# HELM
helm-package:
	helm package $(HELM_CHART_DIR)

helm-push:
	helm push $(HELM_CHART_NAME)-0.1.0.tgz  oci://$(REPOSITORY_HOST)

helm: helm-package helm-push


# Deploy Operator
helm-install:
	helm install --kubeconfig=$(KUBECONFIG) $(HELM_CHART_NAME) oci://$(REPOSITORY_HOST)/$(HELM_CHART_NAME) --version 0.1.0 --namespace $(NAMESPACE) --create-namespace --set serviceUUID=abc

helm-uninstall:
	helm uninstall --kubeconfig=$(KUBECONFIG) $(HELM_CHART_NAME) --namespace $(NAMESPACE)


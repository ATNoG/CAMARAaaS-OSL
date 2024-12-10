# Variables
LOCAL_IMAGE_NAME = ns-ue-operator
LOCAL_TAG = latest

DOCKER_REPOSITORY_IMAGE_NAME = nslice-ue-op
DOCKER_REPOSITORY_TAG = latest
HELM_CHART_NAME = nslice-ue-op-chart
REPOSITORY_HOST = atnog-harbor.av.it.pt/atnog

HELM_CHART_NAME = nslice-ue-op-chart
REPOSITORY_HOST = atnog-harbor.av.it.pt/atnog

KUBECONFIG ?= /etc/rancher/k3s/k3s.yaml 
NAMESPACE = itav-slice-manager-client

PATCH_CONTENT_INVALID='{"spec": {"qodProv": {"newQoDProvToApply": true, "provisioningId": "12345678-1234-1234-1234-123456789abc", "device": {"phoneNumber": "+987654321", "networkAccessIdentifier": "987654321@newdomain.com", "ipv4Address": {"publicAddress": "198.51.100.0", "privateAddress": "192.168.1.200", "privatePort": 6000}, "ipv6Address": "2001:db8::1"}, "qosProfile": "QOS_D"}}}'



# DOCKER

#---docker-build:
#---	docker build -t $(LOCAL_IMAGE_NAME):$(LOCAL_TAG) .
#---
#---docker-tag:
#---	docker tag $(LOCAL_IMAGE_NAME):$(LOCAL_TAG) $(REPOSITORY_HOST)/$(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG)
#---
#---docker-push:
#---	docker push $(REPOSITORY_HOST)/$(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG)
#---
#---docker-clean:
#---	docker image prune -f
#---
#---docker-remove:
#---	docker rmi $(LOCAL_IMAGE_NAME):$(LOCAL_TAG)
#---
#---docker: docker-build docker-tag docker-push


# Local Testing
prepare-local-testing-environment:
	kubectl apply -f ../CR/crd.yaml && kubectl apply -f ./manifests/operator-namespace.yaml && kubectl apply -f ./manifests/operator-role.yaml

terminate-local-testing-environment:
	kubectl delete -f ../CR/crd.yaml && kubectl delete -f ./manifests/operator-namespace.yaml && kubectl delete -f ./manifests/operator-role.yaml

run-local:
	. src/venv/bin/activate && CR_GROUP="av.it.pt" CR_VERSION="v1" CR_PLURAL="ue-qod-profiles" SLICE_MANAGER_BASE_URL="http://10.255.28.64:8080" python3 src/k8s_operator.py


# K8S Manifests
#---create-operator:
#---	kubectl apply -f ./cr/crd.yaml && kubectl apply -f ./k8s/operator-namespace.yaml && kubectl apply -f ./k8s/
#---
#---get-operator-pods:
#---	kubectl get pods -n $(NAMESPACE) -l app=nslice-ue-op -o jsonpath="{.items[0].metadata.name}" 
#---
#---get-operator-logs:
#---	kubectl logs -f $$(kubectl get pods -n $(NAMESPACE)  -l app=nslice-ue-op -o jsonpath="{.items[0].metadata.name}") -n $(NAMESPACE) 
#---
#---delete-operator:
#---	kubectl delete -f ./k8s || true


# K8S Custom Resource
create-crd:
	kubectl apply -f ../CR/crd.yaml

delete-crd:
	kubectl delete -f ../CR/crd.yaml || true

create-cr:
	kubectl apply -f ../CR/cr_init.yaml

delete-cr:
	kubectl delete -f ../CR/cr_init.yaml || true

describe-cr:
	kubectl describe ue-qod-profiles ue-qod-profile-init

patch-cr-invalid: 
	kubectl patch ue-qod-profiles ue-qod-profile-init --namespace=default --type=merge -p $(PATCH_CONTENT_INVALID)

recreate-cr: delete-cr create-cr
recreate-crd: delete-crd create-crd

# HELM
#---helm-package:
#---	helm package $(HELM_CHART_NAME)
#---
#---helm-push:
#---	helm push $(HELM_CHART_NAME)-0.1.0.tgz  oci://$(REPOSITORY_HOST)
#---
#---helm: helm-package helm-push


# Deploy Operator
#---install-operator:
#---	helm install --kubeconfig=$(KUBECONFIG) $(HELM_CHART_NAME) oci://$(REPOSITORY_HOST)/$(HELM_CHART_NAME) --version 0.1.0 --set sliceManagerBaseUrl=http://10.255.28.141:8000 --namespace $(NAMESPACE) --create-namespace
#---
#---uninstall-operator:
#---	helm uninstall --kubeconfig=$(KUBECONFIG) $(HELM_CHART_NAME) --namespace $(NAMESPACE)

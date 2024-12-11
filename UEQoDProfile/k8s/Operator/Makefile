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

PATCH_CONTENT_INVALID='{"spec": {"qodProv": {"operation": "CREATE", "provisioningId": "12345678-1234-1234-1234-12345678901a", "device": {"phoneNumber": "+111111111", "networkAccessIdentifier": "111111111@newdomain.com", "ipv4Address": {"publicAddress": "198.51.100.1", "privateAddress": "192.168.1.1", "privatePort": 1}, "ipv6Address": "2001:db8::1"}, "qosProfile": "QOS_D"}}}'
PATCH_CONTENT_CREATE='{"spec": {"qodProv": {"operation": "CREATE", "provisioningId": "12345678-1234-1234-1234-12345678901b", "device": {"phoneNumber": "+111111112", "networkAccessIdentifier": "111111112@newdomain.com", "ipv4Address": {"publicAddress": "198.51.100.2", "privateAddress": "192.168.1.1", "privatePort": 1}, "ipv6Address": "2001:db8::1"}, "qosProfile": "QOS_A"}}}'
PATCH_CONTENT_UPDATE='{"spec": {"qodProv": {"operation": "UPDATE", "provisioningId": "12345678-1234-1234-1234-12345678901b", "device": {"phoneNumber": "+111111112", "networkAccessIdentifier": "111111112@newdomain.com", "ipv4Address": {"publicAddress": "198.51.100.2", "privateAddress": "192.168.1.1", "privatePort": 1}, "ipv6Address": "2001:db8::1"}, "qosProfile": "QOS_B"}}}'
PATCH_CONTENT_CREATE2='{"spec": {"qodProv": {"operation": "CREATE", "provisioningId": "12345678-1234-1234-1234-12345678901c", "device": {"phoneNumber": "+111111112", "networkAccessIdentifier": "111111112@newdomain.com", "ipv4Address": {"publicAddress": "198.51.100.2", "privateAddress": "192.168.1.1", "privatePort": 1}, "ipv6Address": "2001:db8::1"}, "qosProfile": "QOS_A"}}}'
PATCH_CONTENT_DELETE='{"spec": {"qodProv": {"operation": "DELETE", "provisioningId": "12345678-1234-1234-1234-12345678901b", "device": {"phoneNumber": "+111111112", "networkAccessIdentifier": "111111112@newdomain.com", "ipv4Address": {"publicAddress": "198.51.100.2", "privateAddress": "192.168.1.1", "privatePort": 1}, "ipv6Address": "2001:db8::1"}, "qosProfile": "QOS_B"}}}'



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
	. src/venv/bin/activate && CR_GROUP="av.it.pt" CR_VERSION="v1" CR_PLURAL="ue-qod-profiles" SLICE_MANAGER_BASE_URL="http://10.255.28.64:8080" SLICE_MANAGER_USERNAME="admin" SLICE_MANAGER_PASSWORD="password" python3 src/k8s_operator.py


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

patch-cr-create: 
	kubectl patch ue-qod-profiles ue-qod-profile-init --namespace=default --type=merge -p $(PATCH_CONTENT_CREATE)
	kubectl patch ue-qod-profiles ue-qod-profile-init --namespace=default --type=merge -p $(PATCH_CONTENT_CREATE2)

patch-cr-update: 
	kubectl patch ue-qod-profiles ue-qod-profile-init --namespace=default --type=merge -p $(PATCH_CONTENT_UPDATE)

patch-cr-delete: 
	kubectl patch ue-qod-profiles ue-qod-profile-init --namespace=default --type=merge -p $(PATCH_CONTENT_DELETE)




recreate-cr: delete-cr create-cr
recreate-crd: delete-crd create-crd

sleep:
	sleep 5

test-cr-invalid: recreate-cr patch-cr-invalid describe-cr
test-cr-create: recreate-cr patch-cr-create describe-cr
test-cr-update: recreate-cr patch-cr-create describe-cr sleep patch-cr-update describe-cr

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

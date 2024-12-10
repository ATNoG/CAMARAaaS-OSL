# Variables
LOCAL_IMAGE_NAME = camaraaas-qod-provisioning-api-op-operator
LOCAL_TAG = latest

DOCKER_REPOSITORY_IMAGE_NAME = camaraaas-qod-provisioning-api-op
DOCKER_REPOSITORY_TAG = latest
REPOSITORY_HOST = atnog-harbor.av.it.pt/camaraaas

HELM_CHART_DIR = chart
HELM_CHART_NAME = camaraaas-qod-provisioning-api-op-chart
REPOSITORY_HOST = atnog-harbor.av.it.pt/camaraaas

KUBECONFIG ?= /etc/rancher/k3s/k3s.yaml 
NAMESPACE = itav-slice-manager-client


# DOCKER
#
docker-build:
	docker build -t $(LOCAL_IMAGE_NAME):$(LOCAL_TAG) .

docker-tag:
	docker tag $(LOCAL_IMAGE_NAME):$(LOCAL_TAG) $(REPOSITORY_HOST)/$(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG)

docker-push:
	docker push $(REPOSITORY_HOST)/$(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG)

docker-clean:
	docker image prune -f

docker-remove:
	docker rmi $(LOCAL_IMAGE_NAME):$(LOCAL_TAG)

docker: docker-build docker-tag docker-push


# Local Testing
prepare-local-testing-environment:
	kubectl apply -f ../CR/crd.yaml && kubectl apply -f ./manifests/operator-namespace.yaml && kubectl apply -f ./manifests/operator-role.yaml

terminate-local-testing-environment:
	kubectl delete -f ../CR/crd.yaml && kubectl delete -f ./manifests/operator-namespace.yaml && kubectl delete -f ./manifests/operator-role.yaml

run-local:
	. src/venv/bin/activate && CR_GROUP="av.it.pt" CR_VERSION="v1" CR_PLURAL="camaraaas-qod-provisioning-apis" SLICE_MANAGER_BASE_URL="http://10.255.28.141:8000" python3 src/k8s_operator.py


# K8S Manifests
create-operator:
	kubectl apply -f ../CR/crd.yaml && kubectl apply -f ./manifests/operator-namespace.yaml && kubectl apply -f ./manifests/

get-operator-pods:
	kubectl get pods -n $(NAMESPACE) -l app=camaraaas-qod-provisioning-api-op -o jsonpath="{.items[0].metadata.name}" 

get-operator-logs:
	kubectl logs -f $$(kubectl get pods -n $(NAMESPACE)  -l app=camaraaas-qod-provisioning-api-op -o jsonpath="{.items[0].metadata.name}") -n $(NAMESPACE) 

delete-operator:
	kubectl delete -f ./manifests || true


# K8S Custom Resource
create-crd:
	kubectl apply -f ../CR/crd.yaml

delete-crd:
	kubectl delete -f ../CR/crd.yaml || true

create-cr:
	kubectl apply -f ../CR/cr_simple.yaml

delete-cr:
	kubectl delete -f ../CR/cr_simple.yaml || true

recreate-crd: delete-crd create-crd
recreate-cr: delete-cr create-cr

# HELM
helm-package:
	helm package $(HELM_CHART_DIR)

helm-push:
	helm push $(HELM_CHART_NAME)-0.1.0.tgz  oci://$(REPOSITORY_HOST)

helm: helm-package helm-push


# Deploy Operator
install-operator:
	helm install --kubeconfig=$(KUBECONFIG) $(HELM_CHART_NAME) oci://$(REPOSITORY_HOST)/$(HELM_CHART_NAME) --version 0.1.0 --namespace $(NAMESPACE) --create-namespace

uninstall-operator:
	helm uninstall --kubeconfig=$(KUBECONFIG) $(HELM_CHART_NAME) --namespace $(NAMESPACE)


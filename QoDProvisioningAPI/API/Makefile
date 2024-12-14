
# Variables
DOCKER_REPOSITORY_IMAGE_NAME = camaraaas-qod-provisioning-api
DOCKER_REPOSITORY_TAG = latest
REPOSITORY_HOST = atnog-harbor.av.it.pt/camaraaas

SERVICE_UUID=1450fde5-bae5-4098-9aac-7b713a97a14b

# API
init:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && deactivate

run:
	. venv/bin/activate && SQLITE_DB_PATH=~/sqlite.db  BROKER_ADDRESS=10.255.28.137 BROKER_PORT=61613  BROKER_USERNAME=artemis BROKER_PASSWORD=artemis SERVICE_UUID=$(SERVICE_UUID) PYTHONPATH=src uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level info  && deactivate

delete-db:
	rm -f ~/sqlite.db


# DOCKER
docker-build:
	docker build -t $(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG) .

docker-tag:
	docker tag $(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG) $(REPOSITORY_HOST)/$(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG)

docker-push:
	docker push $(REPOSITORY_HOST)/$(DOCKER_REPOSITORY_IMAGE_NAME):$(DOCKER_REPOSITORY_TAG)

docker-clean:
	docker image prune -f

docker-remove:
	docker rmi $(LOCAL_IMAGE_NAME):$(LOCAL_TAG)

docker: docker-build docker-tag docker-push



SERVICE_UUID=0726c0c2-9fc8-4593-b2e0-8740764ae365

init:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && deactivate

run:
	. venv/bin/activate && SQLITE_DB_PATH=~/sqlite.db  BROKER_ADDRESS=10.255.28.137 BROKER_PORT=61613  BROKER_USERNAME=artemis BROKER_PASSWORD=artemis SERVICE_UUID=$(SERVICE_UUID) PYTHONPATH=src uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level info  && deactivate

delete-db:
	rm -f ~/sqlite.db
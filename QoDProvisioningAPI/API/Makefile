
SERVICE_UUID=9c24ef26-30a0-41ad-855e-6ee1bbf0a627 

init:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && deactivate

run:
	. venv/bin/activate && SQLITE_DB_PATH=~/sqlite.db  BROKER_ADDRESS=10.255.28.137 BROKER_PORT=61613  BROKER_USERNAME=artemis BROKER_PASSWORD=artemis SERVICE_UUID=$(SERVICE_UUID) PYTHONPATH=src uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --log-level info  && deactivate

delete-db:
	rm -f ~/sqlite.db
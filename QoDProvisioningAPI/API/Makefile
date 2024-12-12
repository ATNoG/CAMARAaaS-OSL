
SERVICE_UUID = 

init:
	python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && deactivate

run:
	. venv/bin/activate && SQLITE_DB_PATH=/home/rdireito/sqlite.db  BROKER_ADDRESS=10.255.28.137 BROKER_PORT=61613  BROKER_USERNAME=artemis BROKER_PASSWORD=artemis SERVICE_UUID=$(SERVICE_UUID) uvicorn openapi_server.main:app --host 0.0.0.0 --port 8000 --log-level info  && deactivate
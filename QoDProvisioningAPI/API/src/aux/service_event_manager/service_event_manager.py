import stomp
import json
import threading
import time
import logging
from fastapi.logger import logger 
import os
import threading

from .config import Config

# Set Uvicorn log level
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.INFO)

# Set FastAPI logger level
logger.setLevel(logging.INFO)

# Constants for STOMP service configuration
CATALOG_UPD_SERVICE = "CATALOG.UPD.SERVICE"
EVENT_SERVICE_ATTRCHANGED = "EVENT.SERVICE.ATTRCHANGED"

class ServiceEventManager:
    """Manages event subscriptions and service updates using STOMP."""

    # Validate the environment variables before using them
    Config.validate()

    broker_address = Config.broker_address
    broker_port = Config.broker_port
    broker_username = Config.broker_username
    broker_password = Config.broker_password
    service_uuid = Config.service_uuid

    # Initialize a shared dictionary for storing results
    camara_results = {}
    camara_results_lock = threading.Lock()

    @classmethod
    def subscribe_to_events(cls):
        """Subscribe to the events topic."""

        def run_listener():
            conn = stomp.Connection([(cls.broker_address, cls.broker_port)], heartbeats=(15000, 15000))
            conn.set_listener('', cls.MyListener())
            conn.connect(cls.broker_username, cls.broker_password, wait=True)
            conn.subscribe(destination=EVENT_SERVICE_ATTRCHANGED, id=1)

            logger.info(f"Subscribed to {EVENT_SERVICE_ATTRCHANGED}. Waiting for messages...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Disconnecting listener...")
                conn.disconnect()

        listener_thread = threading.Thread(target=run_listener)
        listener_thread.daemon = True  # Allow program to exit even if thread is running
        listener_thread.start()

    @classmethod
    def update_service(cls, update_payload):
        """Send a service update to the specified destination."""
        try:
            headers = {
                "serviceid": cls.service_uuid,
                "triggerServiceActionQueue": True
            }

            # Connect to STOMP broker and send the message
            conn = stomp.Connection([(cls.broker_address, cls.broker_port)])
            conn.connect(cls.broker_username, cls.broker_password, wait=True)

            logger.info(f"Sending update to {CATALOG_UPD_SERVICE}...")
            conn.send(destination=CATALOG_UPD_SERVICE, body=json.dumps(update_payload), headers=headers)
            logger.info("Update sent successfully.")
            
            conn.disconnect()
        except Exception as e:
            logger.error(f"Cannot update Service: {cls.service_uuid}: {str(e)}")

    class MyListener(stomp.ConnectionListener):
        """Custom listener to handle incoming messages from the STOMP broker."""

        def __init__(self):
            super().__init__()

        def on_message(self, frame):
            """Handle received message frames."""

            # Attempt to parse the body as JSON
            try:
                message = json.loads(frame.body)

                service_info = message.get("event").get("service")
                
                if service_info.get("uuid") == ServiceEventManager.service_uuid:
                    for characteristic in service_info.get("serviceCharacteristic"):
                        if characteristic.get("name") == "camaraResults":
                            characteristic_value = characteristic.get("value").get("value")

                            with ServiceEventManager.camara_results_lock:
                                ServiceEventManager.camara_results["camaraResults"] = characteristic_value
                            logger.info(f"New camaraResults stored for UUID {service_info.get('uuid')}: {characteristic_value}\n")


            except json.JSONDecodeError:
                print('Received message is not valid JSON.')

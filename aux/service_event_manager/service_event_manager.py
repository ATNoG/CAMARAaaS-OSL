import stomp
import json
import threading
import time
import logging
import os

# Configure logging for better debug visibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for STOMP service configuration
CATALOG_UPD_SERVICE = "CATALOG.UPD.SERVICE"
EVENT_SERVICE_ATTRCHANGED = "EVENT.SERVICE.ATTRCHANGED"

class ServiceEventManager:
    """Manages event subscriptions and service updates using STOMP."""

    broker_address = os.getenv('BROKER_ADDRESS')
    broker_port = os.getenv('BROKER_PORT')
    broker_username = os.getenv('BROKER_USERNAME') 
    broker_password = os.getenv('BROKER_PASSWORD') 

    print(f"Using broker address: {broker_address}")

    @classmethod
    def subscribe_to_events(cls, service_uuid):
        """Subscribe to the events topic."""

        def run_listener():
            conn = stomp.Connection([(cls.broker_address, cls.broker_port)], heartbeats=(15000, 15000))
            conn.set_listener('', cls.MyListener(service_uuid))
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
    def update_service(cls, service_uuid, update_payload):
        """Send a service update to the specified destination."""
        try:
            headers = {
                "serviceid": service_uuid,
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
            logger.error(f"Cannot update Service: {service_uuid}: {str(e)}")

    class MyListener(stomp.ConnectionListener):
        """Custom listener to handle incoming messages from the STOMP broker."""

        def __init__(self, service_uuid):
            super().__init__()
            self.service_uuid = service_uuid

        def on_message(self, frame):
            """Handle received message frames."""

            # Attempt to parse the body as JSON
            try:
                message = json.loads(frame.body)

                service_info = message.get("event").get("service")

                service_is_CFS = True if service_info.get("@type") == "CustomerFacingService" else False
                print(f"ESTE E O SERVICE UUID {self.service_uuid}")
                service_has_correct_uuid = True if service_info.get("uuid") == self.service_uuid else False

                if service_is_CFS and service_has_correct_uuid:
                    for characteristic in service_info.get("serviceCharacteristic"):
                        if characteristic.get("name") == "camaraAPI.Results":
                            characteristic_value = characteristic.get("value").get("value")
                            logger.info('new camaraAPI.Results: {}'.format(characteristic_value))

            except json.JSONDecodeError:
                print('Received message is not valid JSON.')

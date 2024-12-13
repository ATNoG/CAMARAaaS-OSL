import stomp
import json
import time
import os
import asyncio

from aux.config import Config

# Set up logging
logger = Config.setup_logging()

# Constants for STOMP service configuration
CATALOG_UPD_SERVICE = "CATALOG.UPD.SERVICE"
EVENT_SERVICE_ATTRCHANGED = "EVENT.SERVICE.ATTRCHANGED"

class ServiceEventManager:
    """Manages event subscriptions and service updates using STOMP."""

    # Validate the environment variables before using them
    Config.validate()

    camara_results_queue = None
    camara_results_lock = None

    @classmethod
    def initialize(cls):
        cls.broker_address = Config.broker_address
        cls.broker_port = Config.broker_port
        cls.broker_username = Config.broker_username
        cls.broker_password = Config.broker_password
        cls.service_uuid = Config.service_uuid

        """Initialize shared resources."""
        cls.camara_results_queue = asyncio.Queue()
        cls.camara_results_lock = asyncio.Lock()


    @classmethod
    def subscribe_to_events(cls):
        """Subscribe to the events topic."""

        loop = asyncio.get_event_loop()

        def run_listener():
            conn = stomp.Connection(
                [(cls.broker_address, cls.broker_port)], 
                heartbeats=(15000, 15000)
            )
            conn.set_listener('', cls.MyListener(loop))
            conn.connect(
                cls.broker_username, 
                cls.broker_password, 
                wait=True
            )
            conn.subscribe(destination=EVENT_SERVICE_ATTRCHANGED, id=1)

            logger.info(
                f"Subscribed to {EVENT_SERVICE_ATTRCHANGED}. " 
                f"Waiting for messages..."
            )

        # Run the listener in a separate thread
        import threading
        listener_thread = threading.Thread(target=run_listener, daemon=True)
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
            conn.connect(
                cls.broker_username, 
                cls.broker_password, 
                wait=True
            )

            logger.info(f"Sending update to {CATALOG_UPD_SERVICE}...")
            conn.send(
                destination=CATALOG_UPD_SERVICE, 
                body=json.dumps(update_payload), 
                headers=headers
            )
            logger.info("Update sent successfully.")
            
            conn.disconnect()
        except Exception as e:
            logger.error(f"Cannot update Service: {cls.service_uuid}: {str(e)}")

    class MyListener(stomp.ConnectionListener):
        """Custom listener to handle incoming messages from the STOMP broker."""

        def __init__(self, loop):
            super().__init__()
            self.loop = loop

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

                            # Add the result to the async queue
                            asyncio.run_coroutine_threadsafe(
                                ServiceEventManager.camara_results_queue.put(characteristic_value),
                                self.loop
                            )

            except json.JSONDecodeError:
                print('Received message is not valid JSON.')
import stomp
import json
import time
import os
import asyncio
from functools import wraps
from config import Config

# Set up logging
logger = Config.setup_logging()

# Constants for STOMP service configuration
CATALOG_UPD_SERVICE = "CATALOG.UPD.SERVICE"
EVENT_SERVICE_ATTRCHANGED = "EVENT.SERVICE.ATTRCHANGED"
# TODO: move these variables to config

def check_subscribe_connection(method):
    @wraps(method)
    def wrapper(cls, *args, **kwargs):
        if not cls.connection or not cls.connection.is_connected():
            logger.warning("Connection not active. Reconnecting...")
            cls.connection = stomp.Connection(
                [(cls.broker_address, cls.broker_port)], 
                heartbeats=(15000, 15000)
            )
            cls.connection.connect(
                cls.broker_username, 
                cls.broker_password, 
                wait=True
            )
            if cls.connection and cls.connection.is_connected():
                logger.info("Connection is active.")
        return method(cls, *args, **kwargs)
    return wrapper

class ServiceEventManager:
    """Manages event subscriptions and service updates using STOMP."""

    # Validate the environment variables before using them
    Config.validate()

    camara_results_queue = None
    camara_results_lock = None
    connection = None

    @classmethod
    def initialize(cls):
        cls.broker_address = Config.broker_address
        cls.broker_port = Config.broker_port
        cls.broker_username = Config.broker_username
        cls.broker_password = Config.broker_password
        cls.service_uuid = Config.service_uuid

        # Initialize shared resources
        cls.camara_results_queue = asyncio.Queue()
        cls.camara_results_lock = asyncio.Lock()
        
        


    @classmethod
    @check_subscribe_connection
    def subscribe_to_events(cls):
        """Subscribe to the events topic."""

        loop = asyncio.get_event_loop()

        def run_listener():
            cls.connection.set_listener('', cls.MyListener(loop))
            cls.connection.subscribe(
                destination=EVENT_SERVICE_ATTRCHANGED,
                id=1
            )

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
            
        def get_camara_results(self, service_info):
            for charact in service_info.get("serviceCharacteristic"):
                if charact.get("name") == "camaraResults":
                    return charact.get("value").get("value")

        def on_message(self, frame):
            """Handle received message frames."""

            # Attempt to parse the body as JSON
            try:
                message = json.loads(frame.body)
                service_info = message.get("event").get("service")
                
                camara_results = None
                if service_info.get("uuid") == ServiceEventManager.service_uuid:
                    camara_results = self.get_camara_results(service_info)

                # Add the result to the async queue
                if camara_results:
                    asyncio.run_coroutine_threadsafe(
                        ServiceEventManager.camara_results_queue.put(
                            camara_results
                        ),
                        self.loop
                    )

            except json.JSONDecodeError:
                logger.info('Received message is not valid JSON.')
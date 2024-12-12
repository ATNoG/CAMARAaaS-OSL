import os
import argparse
import threading
from service_event_manager import ServiceEventManager

# Set environment variables for the demo (replace with actual values)
os.environ['BROKER_ADDRESS'] = '10.255.28.137'
os.environ['BROKER_PORT'] = '61613'
os.environ['BROKER_USERNAME'] = 'artemis'
os.environ['BROKER_PASSWORD'] = 'artemis'

def start_subscription():
    print("Starting subscription to events...")
    ServiceEventManager.subscribe_to_events("8958bcdc-8421-4ccd-b953-74d486f93424")
    print("Subscription thread running.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Service Event Manager CLI")
    parser.add_argument("action", choices=["subscribe", "update"], help="Action to perform: subscribe to events or update a service")
    parser.add_argument("--service_uuid", type=str, help="Service UUID for updating a service", required=False)
    parser.add_argument("--payload", type=str, help="Update payload as a JSON string", required=False)

    args = parser.parse_args()

    if args.action == "subscribe":
        subscription_thread = threading.Thread(target=start_subscription)
        subscription_thread.daemon = True  # Allow program to exit even if thread is running
        subscription_thread.start()

        print("Press Ctrl+C to exit subscription mode or run 'update' commands in another terminal.")
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Exiting subscription mode...")

    elif args.action == "update":
        if not args.service_uuid or not args.payload:
            print("Error: Both --service_uuid and --payload are required for updating a service.")
            exit(1)

        try:
            print("Sending service update...")
            ServiceEventManager.update_service(args.service_uuid, eval(args.payload))
            print("Service update sent successfully.")
        except Exception as e:
            print(f"Error while sending service update: {e}")
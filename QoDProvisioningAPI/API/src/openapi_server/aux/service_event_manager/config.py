import os

class Config():

    broker_address = os.getenv('BROKER_ADDRESS')
    broker_port = os.getenv('BROKER_PORT')
    broker_username = os.getenv('BROKER_USERNAME') 
    broker_password = os.getenv('BROKER_PASSWORD') 
    service_uuid = os.getenv('SERVICE_UUID')

    @classmethod
    def validate(cls):
        missing_envs = []

        for var in ['broker_address', 'broker_port', 'broker_username', 
                        'broker_password', 'service_uuid']:
            if getattr(cls, var) is None:
                missing_envs.append(var.upper())

        if missing_envs:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_envs)}"
            )

        print("All required environment variables are set.")
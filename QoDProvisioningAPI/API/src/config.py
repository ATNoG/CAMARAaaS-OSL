import os
import sys
import logging

class Config():

    broker_address = os.getenv('BROKER_ADDRESS')
    broker_port = os.getenv('BROKER_PORT')
    broker_username = os.getenv('BROKER_USERNAME') 
    broker_password = os.getenv('BROKER_PASSWORD') 
    service_uuid = os.getenv('SERVICE_UUID')
    log_level = os.getenv('LOG_LEVEL', "INFO")
    db_path = os.getenv("SQLITE_DB_PATH", "/data/sqlite.db")

    logger = None

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

    @classmethod
    def setup_logging(cls):
        if cls.logger is None:
            log_level = getattr(logging, cls.log_level.upper())
            
            # Create a logger
            cls.logger = logging.getLogger()
            cls.logger.setLevel(log_level)

            # Create a stream handler that outputs to stdout
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)

            # Create a formatter and add it to the handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

            # Add the handler to the logger
            cls.logger.addHandler(handler)

        return cls.logger
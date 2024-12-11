from datetime import datetime, timezone
from datetime import datetime, timezone
import requests
import json
import time

from config import Config


# Set up logging
logger = Config.setup_logging()

class ITAvNetworkSliceManager:
    
    # Set up logging
    #logger = Config.setup_logging()

    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def patch_ue_profile(self, payload) -> bool:

        logger.info(
            "Will Try to Patch ta UE Pofile with Characteristics: "
            f"{json.dumps(payload, indent=4)}"
        )

        try:
            response = requests.request(
                "PATCH",
                f"{self.base_url}/UE/patch",
                headers= {
                    'Content-Type': 'application/json'
                },
                auth=(self.username, self.password),
                data= json.dumps(payload),
                timeout=30
            )
            
            logger.info(
                "Slice Manager API responded with status code: "
                f"{response.status_code}."
            )
            
                        
            if response.status_code == 200:
                return True
            else:
                return False

        except Exception as exception:
            logger.error(f"An Exception Ocurred: {exception}")
            return False
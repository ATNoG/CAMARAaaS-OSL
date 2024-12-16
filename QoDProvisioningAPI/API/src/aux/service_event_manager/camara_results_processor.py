# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024

import asyncio

from aux.service_event_manager.service_event_manager import ServiceEventManager
from config import Config
import json
from database import crud
from database.db import get_db
from aux.constants import Constants
# Set up logging
logger = Config.setup_logging()

class CamaraResultsProcessor:
    """Handles processing of camara results from the queue."""

    def __init__(self, queue):
        self.queue = queue
        self.db_session = next(get_db())

    async def process_results(self):
        """Continuously processes results from the queue."""
        try:
            results = None
            # Enter the infinite loop to process subsequent results
            while True:
                results_str = await self.queue.get()
                try:
                    results = json.loads(results_str)
                except Exception as e:
                    logger.error(
                        f"Could not parse Camara results. Reason: {e}"
                    )
                logger.info(
                    f"Amounf of processed CAMARA Results: {len(results)}."
                )
                logger.debug(f"Processed camaraResults: {results}")
                
                self.update_provisionings(results)
        except asyncio.CancelledError:
            logger.info("CamaraResultsProcessor stopped gracefully.")
        except Exception as e:
            logger.error(f"Error processing camara results: {e}", exc_info=True)

    def update_provisionings(self, current_results):
        Constants.processed_camara_results = []
        for result in current_results:
            try:
                prov_id = result["provisioningId"]
                prov_status = result["status"]
                prov_timestamp =  result["startedAt"]
                crud.update_provisioning_by_id(
                    self.db_session,
                    prov_id,
                    prov_status,
                    prov_timestamp
                    
                )
                # Deal with camara-current-results endpoint 
                if "sinkCredential" in result:
                    if "credentialType" in result["sinkCredential"] \
                    and result["sinkCredential"]["credentialType"] not in \
                    ['PLAIN', 'ACCESSTOKEN', 'REFRESHTOKEN']:
                        result["sinkCredential"]["credentialType"] = None
                    else:
                        result["sinkCredential"] = {
                            "credentialType": None
                        }
                Constants.processed_camara_results.append(result)
            except Exception as e:
                logger.error(
                    f"Could not process CAMARA Result: {result}. Reason: {e}"
                )
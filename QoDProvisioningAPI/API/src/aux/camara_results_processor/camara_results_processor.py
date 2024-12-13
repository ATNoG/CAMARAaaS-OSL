import asyncio

from aux.service_event_manager.service_event_manager import ServiceEventManager
from aux.config import Config

# Set up logging
logger = Config.setup_logging()

class CamaraResultsProcessor:
    """Handles processing of camara results from the queue."""

    def __init__(self, queue):
        self.queue = queue

    async def process_results(self):
        """Continuously processes results from the queue."""
        try:
            # Process the first result
            results = await self.queue.get()
            logger.info(f"Processed camaraResults: {results}")

            # Enter the infinite loop to process subsequent results
            while True:
                results = await self.queue.get()
                logger.info(f"Processed camaraResults: {results}")
        except asyncio.CancelledError:
            logger.info("CamaraResultsProcessor stopped gracefully.")
        except Exception as e:
            logger.error(f"Error processing camara results: {e}", exc_info=True)

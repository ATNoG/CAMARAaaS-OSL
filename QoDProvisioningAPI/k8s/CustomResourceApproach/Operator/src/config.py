# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024
import logging
import os
import sys

class Config():
    # Set up custom resources info
    cr_group = os.getenv('CR_GROUP')
    cr_version = os.getenv('CR_VERSION')
    cr_plural = os.getenv('CR_PLURAL')

    # CAMARA API to be deployed
    camara_api_docker_image = os.getenv('CAMARA_API_DOCKER_IMAGE')
    camara_api_docker_image_port = int(
        os.getenv('CAMARA_API_DOCKER_IMAGE_PORT')
    )
        
    logger = None
    
    # Logging
    @classmethod
    def setup_logging(cls):
        if cls.logger is None:

            log_level = os.getenv('LOG_LEVEL', 'INFO')
            log_level = getattr(logging, log_level.upper())
            
            # Create a logger
            cls.logger = logging.getLogger()
            cls.logger.setLevel(log_level)

            # Create a stream handler that outputs to stdout
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)

            # Create a formatter and add it to the handler
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)

            # Add the handler to the logger
            cls.logger.addHandler(handler)

        return cls.logger
    
    @staticmethod
    def cluster():
        """Name of the cluster"""
        return os.getenv('CLUSTER_NAME')
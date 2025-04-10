import kopf
import json
from kubernetes import client, config, watch
from kubernetes.client import CoreV1Api
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.models.v1_container_status import V1ContainerStatus
import time

from config import Config
from ue_qod_profile_cr_handler import UEQoDProfileCRHandler
from itav_network_slice_manager import ITAvNetworkSliceManager

# Set up logging
logger = Config.setup_logging()

cluster = Config.cluster()

# To store the resource version for each resource to prevent duplicate processing
#processed_resource_versions = {}

def kubeconfig() -> client.CoreV1Api:
    """This is for using the kubeconfig to auth with the k8s api
    with the first try it will try to use the in-cluster config (so for in cluster use)
    If it cannot find an incluster because it is running locally, it will use your local config"""
    try:
        config.load_incluster_config()
        logger.info("Loaded in-cluster configuration.")
    except config.ConfigException as e:
        logger.warning("Failed to load in-cluster config, attempting local kubeconfig.")
        try:
            config.load_kube_config(context=cluster)
            logger.info(f"Loaded kubeconfig file with context {cluster}.")
        except config.ConfigException as e:
            logger.error("Failed to load kubeconfig: ensure your kubeconfig is valid.")
            raise

    # Now you can use the client
    api = client.CoreV1Api()
    return api

@kopf.on.create(Config.cr_group, Config.cr_version, Config.cr_plural)
def on_create_ue_qod_profle(spec, meta, logger, **kwargs):
    logger.info(f"CREATED CR - {meta.get('uid')}")
    ue_qod_prfile_cr_handler.process_ue_qod_profle_event("CREATE", spec, meta)

@kopf.on.update(Config.cr_group, Config.cr_version, Config.cr_plural)
def on_update_ue_qod_profle(spec, old, new, diff, meta, logger, **kwargs):
    logger.info(f"UPDATED CR - {meta.get('uid')}")
    ue_qod_prfile_cr_handler.process_ue_qod_profle_event("UPDATE", spec, meta)
    
@kopf.on.delete(Config.cr_group, Config.cr_version, Config.cr_plural)
def on_delete_ue_qod_profle(meta, spec, logger, **kwargs):
    ue_qod_prfile_cr_handler.process_ue_qod_profle_event("DELETE", spec, meta)

    
@kopf.on.event(Config.cr_group, Config.cr_version, Config.cr_plural)
def log_all_events(event, **kwargs):
    """Logs all events for the given resources."""
    event_type = event.get('type')
    body = event.get('object')
    logger.info(f"EVENT={event_type}, BODY={body}")

def main():
    kopf.run()
    
if __name__ == '__main__':
    v1 = kubeconfig()
    custom_api = client.CustomObjectsApi()
    ue_qod_prfile_cr_handler = UEQoDProfileCRHandler(
        ITAvNetworkSliceManager(
            Config.slice_manager_base_url,
            Config.slice_manager_username,
            Config.slice_manager_password
        ),
        custom_api
    )
    main()
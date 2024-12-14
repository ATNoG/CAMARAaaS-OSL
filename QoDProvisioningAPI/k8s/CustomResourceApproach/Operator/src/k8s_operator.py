import kopf
import json
from kubernetes import client, config, watch
from kubernetes.client import CoreV1Api
from kubernetes.client.models.v1_pod import V1Pod
from kubernetes.client.models.v1_container_status import V1ContainerStatus
import time

from config import Config
from camaraaas_cr_handler import CAMARAaaSQoDProvisioningAPICRHandler

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
def on_create_camaraaas_qod_prov_api(spec, meta, logger, **kwargs):
    camaraaas_handler.process_camaraaas_qod_prov_api("ADD", spec, meta)

@kopf.on.update(Config.cr_group, Config.cr_version, Config.cr_plural)
def on_update_camaraaas_qod_prov_api(spec, old, new, diff, meta, logger, **kwargs):
    camaraaas_handler.process_camaraaas_qod_prov_api("UPDATE", spec, meta)

@kopf.on.delete(Config.cr_group, Config.cr_version, Config.cr_plural)
def on_delete_camaraaas_qod_prov_api(spec, old, new, diff, meta, logger, **kwargs):
    camaraaas_handler.process_camaraaas_qod_prov_api("DELETE", spec, meta)

@kopf.timer(Config.cr_group, Config.cr_version, Config.cr_plural, interval=15)
def periodic_operation(spec, meta, status, namespace, logger, **kwargs):
    camaraaas_handler.update_camara_results(spec, meta)

def main():
    kopf.run()
    
if __name__ == '__main__':
    v1 = kubeconfig()
    custom_api = client.CustomObjectsApi()
    camaraaas_handler = CAMARAaaSQoDProvisioningAPICRHandler(custom_api, v1)
    main()
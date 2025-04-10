# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024
import kopf
from kubernetes import client, config, watch
from kubernetes.client import CoreV1Api
from kubernetes.client import CustomObjectsApi
import requests
import json 
from config import Config

# Set up logging
logger = Config.setup_logging()

class CAMARAaaSQoDProvisioningAPICRHandler:

    def __init__(
        self,
        custom_objects_api: CustomObjectsApi,
        core_api: CoreV1Api
    ):
        self.custom_objects_api = custom_objects_api
        self.core_api = core_api
        
    def process_camaraaas_qod_prov_api(
        self, event: str, spec: dict, metadata: dict
        ) -> None:

        cr_name = metadata['name']
        cr_namespace = metadata['namespace']
        cr_uuid = metadata['uid']

        if event == "ADD":
            logger.info(
                f"A resource with group: {Config.cr_group}, "
                f"version: {Config.cr_version}, plural: {Config.cr_plural} "
                f"was CREATED. This resource is named '{cr_name}' and was "
                f"deployed in namespace '{cr_namespace}'. Will now create a "
                "a pod and a service to offer this resource"
            )
            self._deploy_CAMARAaaS(cr_uuid, cr_name, cr_namespace, spec)
        
        elif event == "UPDATE":
            logger.info(
                f"A resource with group: {Config.cr_group}, "
                f"version: {Config.cr_version}, plural: {Config.cr_plural} "
                f"was UPDATED. This resource is named '{cr_name}' and was "
                f"deployed in namespace '{cr_namespace}'. "
                f"Resource: {spec}."
            )
            
        elif event == "DELETE":
            logger.info(
                f"A resource with group: {Config.cr_group}, "
                f"version: {Config.cr_version}, plural: {Config.cr_plural} "
                f"was DELETED. This resource was named '{cr_name}' and was "
                f"deployed in namespace '{cr_namespace}'. Will now delete its "
                "artifacts"
            )
            self._delete_CAMARAaaS(cr_uuid, cr_name, cr_namespace)
        
 
    def update_camara_results(self, spec, metadata):
        if "camaraAPI" in spec:
            try:
                response = requests.get(
                    f"{spec['camaraAPI']['url']}/osl/current-camara-results"
                )
                # Validate the HTTP response status
                if response.status_code == 200:
                    results = response.json()
                    logger.info(f"Processed CAMARA Results: {results}")
                    self._process_obtained_camara_results(
                        metadata['namespace'],
                        metadata['name'],
                        results
                    )
                else:
                    logger.error(
                        "Could not obtain processed CAMARA Results "
                        f"for the API available at {spec['camaraAPI']['url']}. "
                        f"Got HTTP Status Code {response.status_code}. "
                        f"Response Text: {response.text}"
                    )
            except Exception as e:
                logger.error(
                        "Could not obtain processed CAMARA Results "
                        f"for the API available at {spec['camaraAPI']['url']}. "
                        f"Reason: {e}."
                    )
                
 
    def _deploy_CAMARAaaS(self, cr_uuid, cr_name, cr_namespace, spec):
        pod_name = f"camara-{cr_uuid}-pod"
        service_name = f"camara-{cr_uuid}-service"
        app_label = f"camara-{cr_uuid}-app"
        
        # 1. Deploy the Pod
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": pod_name,
                "labels": {"app": app_label}
            },
            "spec": {
                "containers": [{
                    "name": "app-container",
                    "image": f"{Config.camara_api_docker_image}",
                    "ports": [
                        {"containerPort": Config.camara_api_docker_image_port}
                    ],
                    "env": [
                        {
                            "name": "BROKER_ADDRESS",
                            "value": spec["messageBroker"]["address"]
                        },
                        {
                            "name": "BROKER_PORT",
                            "value": str(spec["messageBroker"]["port"])
                        },
                        {
                            "name": "BROKER_USERNAME",
                            "value": spec["messageBroker"]["username"]
                        },
                        {
                            "name": "BROKER_PASSWORD",
                            "value": spec["messageBroker"]["password"]
                        },
                        {
                            "name": "SERVICE_UUID",
                            "value": spec["serviceUnderControl"]["uuid"]
                        }
                    ]
                }]
            }
        }
        self.core_api.create_namespaced_pod(
            namespace=cr_namespace, body=pod_manifest
        )
        
        # 2. Create a NodePort Service
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": service_name},
            "spec": {
                "selector": {"app": app_label},
                "ports": [
                    {
                        "port": Config.camara_api_docker_image_port,
                        "targetPort": Config.camara_api_docker_image_port
                    }
                ],
                "type": "NodePort"
            }
        }
        service = self.core_api.create_namespaced_service(
            namespace=cr_namespace,
            body=service_manifest
        )

        # 3. Determine the random NodePort assigned
        node_port = service.spec.ports[0].node_port
        nodes = self.core_api.list_node().items
        if not nodes:
            raise kopf.PermanentError("No nodes found in the cluster.")
        node_ip = next(
            (
                addr.address
                for addr in nodes[0].status.addresses
                if addr.type == "InternalIP"
            ), None
        )
        
        if not node_ip:
            raise kopf.PermanentError("No internal node IP found.")
        
        url = f"http://{node_ip}:{node_port}"
        
        logger.info(f"CAMARA QoD Provisioning API deployed at: {url}")
        self._process_successful_deployment(cr_namespace, cr_name, url)
            

    def _delete_CAMARAaaS(self, cr_uuid, cr_name, cr_namespace):
        pod_name = f"camara-{cr_uuid}-pod"
        service_name = f"camara-{cr_uuid}-service"
        app_label = f"camara-{cr_uuid}-app"
        
        # 1. Delete the Pod
        try:
            self.core_api.delete_namespaced_pod(
                name=pod_name,
                namespace=cr_namespace
            )
            logger.info(f"Pod {pod_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            if e.status == 404:
                logger.info(f"Pod {pod_name} not found. Skipping deletion.")
            else:
                raise

        # 2. Delete the Service
        try:
            self.core_api.delete_namespaced_service(
                name=service_name,
                namespace=cr_namespace
            )
            logger.info(f"Service {service_name} deleted successfully.")
        except client.exceptions.ApiException as e:
            if e.status == 404:
                logger.info(f"Service {service_name} not found.")
            else:
                raise

    
    def _process_successful_deployment(self, namespace, name, url):
        patch = {
            "spec": {
                "camaraAPI": {
                    "status": "RUNNING",
                    "url": url,
                    "username": "Not Applicable",
                    "password": "Not Applicable"
                }
            }
        }
        
        try:
            # Apply the patch to update 'spec.data2' of the custom resource
            self.custom_objects_api.patch_namespaced_custom_object(
                group=Config.cr_group,
                version=Config.cr_version,
                namespace=namespace,
                plural=Config.cr_plural,
                name=name,
                body=patch
            )
            logger.info(
                f"Updated 'spec.camaraAPI' for {name} in "
                f"{namespace} to {patch}")

        except client.exceptions.ApiException as e:
            logger.error(
                "Exception when updating 'spec.camaraAPI' "
                f"in custom resource: {e}")
    

    def _process_obtained_camara_results(self, namespace, name, results):
        patch = {
            "spec": {
                "camaraAPI": {
                    "results": json.dumps(results)
                }
            }
        }
    
        try:
            # Apply the patch to update 'spec.data2' of the custom resource
            self.custom_objects_api.patch_namespaced_custom_object(
                group=Config.cr_group,
                version=Config.cr_version,
                namespace=namespace,
                plural=Config.cr_plural,
                name=name,
                body=patch
            )
            logger.info(
                f"Updated 'spec.camaraAPI.results' for {name} in "
                f"{namespace} to {patch}")

        except client.exceptions.ApiException as e:
            logger.error(
                "Exception when updating 'spec.camaraAPI.results' "
                f"in custom resource: {e}")
    


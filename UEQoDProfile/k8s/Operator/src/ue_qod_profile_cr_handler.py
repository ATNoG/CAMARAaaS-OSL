import kopf
from kubernetes import client, config, watch
from kubernetes.client import CoreV1Api
import requests
import json 
from datetime import datetime
import copy
from config import Config
from itav_network_slice_manager import ITAvNetworkSliceManager

# Set up logging
logger = Config.setup_logging()

class UEQoDProfileCRHandler:

    def __init__(
        self,
        slice_manager: ITAvNetworkSliceManager,
        custom_objects_api: CoreV1Api
    ):
        self.slice_manager = slice_manager
        self.custom_objects_api = custom_objects_api
        self.results_cache = {}
        
    def process_ue_qod_profle_event(
        self, event: str, spec: dict, metadata: dict
        ) -> None:

        cr_name = metadata['name']
        cr_namespace = metadata['namespace']

        if event == "DELETE":
            logger.info(
                f"A resource with group: {Config.cr_group}, "
                f"version: {Config.cr_version}, plural: {Config.cr_plural} "
                f"was DELETED. This resource was named '{cr_name}' and was "
                f"deployed in namespace '{cr_namespace}'."
            )
            del self.results_cache[f"{cr_namespace}/{cr_name}"]
            logger.info(
                f"Updated Results Cache After Deletion: {self.results_cache}"
            )
            return
            
        elif event == "CREATE":
            logger.info(
                f"A resource with group: {Config.cr_group}, "
                f"version: {Config.cr_version}, plural: {Config.cr_plural} "
                f"was CREATED. This resource is named '{cr_name}' and was "
                f"deployed in namespace '{cr_namespace}'. Will now parse this "
                "resource and  request the creation of a QoD UE Profile via "
                f"ITAvNetworkSliceManager (url={self.slice_manager.base_url})"
                f"Resource: {spec}"
            )
            self._process_init(cr_namespace, cr_name)
            
        elif event == "UPDATE":
            logger.info(
                f"A resource with group: {Config.cr_group}, "
                f"version: {Config.cr_version}, plural: {Config.cr_plural} "
                f"was UPDATED. This resource is named '{cr_name}' and was "
                f"deployed in namespace '{cr_namespace}'. "
                f"Resource: {spec}"
            )    
        
        # If there is not a new profile to apply, stop
        if "qodProv" not in spec \
        or spec["qodProv"].get("operation") \
        not in ["CREATE", "UPDATE", "DELETE"]:
            logger.info(
                "It is not required to provision a new QoD profile."
            )
            return
        
        tmp_result = self._spec_qod_prov_to_tmp_result(spec)
        
        self._process_qod_provisioning_request(
            cr_namespace, cr_name, spec, tmp_result
        )
    
    def _process_qod_provisioning_request (
        self, cr_namespace, cr_name, spec, tmp_result
    ):  
        # Check if profile exists
        # If the profile does not exist, set the status as UNAVAILABLE,
        # update the results, and return
        if spec["qodProv"]["qosProfile"] \
        not in spec["ITAvSliceManager"]["profiles"]:
            logger.info(
                f"The profile {spec['qodProv']['qosProfile']} does not exist!"
            )

            tmp_result["status"] = "UNAVAILABLE"
            tmp_result["startedAt"] = datetime\
                .utcnow().isoformat(timespec='seconds') + 'Z'

            self._process_results_update(
                cr_namespace, cr_name, spec, tmp_result,
                spec["qodProv"].get("operation")
            )
        
        # If the profile exists, try to apply it via the Slice Manager
        else:
            tmp_result["status"] = "UNAVAILABLE"

            if spec["qodProv"].get("operation") in ["CREATE", "UPDATE"]:
                payload = self._spec_params_to_ue_patch_payload(spec)
    
                if self.slice_manager.patch_ue_profile(payload):
                    tmp_result["status"] = "AVAILABLE"

                tmp_result["startedAt"] = datetime\
                    .utcnow().isoformat(timespec='seconds') + 'Z'    
            
            elif spec["qodProv"].get("operation") == "DELETE":
                spec["qodProv"]["qosProfile"] == "default"
                payload = self._spec_params_to_ue_patch_payload(spec)
                self.slice_manager.patch_ue_profile(payload)
                
            self._process_results_update(
                cr_namespace, cr_name, spec, tmp_result,
                spec["qodProv"].get("operation")
            )
        
    
    def _spec_qod_prov_to_tmp_result(self, spec):
        tmp_result = copy.deepcopy(spec["qodProv"])
        del tmp_result["operation"]
        return tmp_result
    
    def _spec_params_to_ue_patch_payload(self, spec):

        qod_prov = spec["qodProv"]
        net_slice = spec["ITAvSliceManager"]["slice"]
        profiles = spec["ITAvSliceManager"]["profiles"]

        if qod_prov["qosProfile"] == "default":
            ambrup = int(profiles.get(qod_prov["qosProfile"]).get("AMBRUP"))
            ambrdw = int(profiles.get(qod_prov["qosProfile"]).get("AMBRDW"))
        else:
            ambrup = int(spec["ITAvSliceManager"]["defaultProfile"]["AMBRUP"])
            ambrdw = int(spec["ITAvSliceManager"]["defaultProfile"]["AMBRDW"])

        # Generated by AI
        payload = {
            "IMSI": int(
                qod_prov["device"]["networkAccessIdentifier"]\
                .split("@")[0]
            ),
            "numIMSIs": 1,
            "slice": net_slice,
            "IPV4": "",
            "IPV6":  "",
            "AMDATA": True,
            "DEFAULT": "TRUE",
            "UEcanSendSNSSAI": "TRUE",
            "AMBRUP": ambrup,
            "AMBRDW": ambrdw
        }

        # Remove any keys where the value is None
        payload = {k: v for k, v in payload.items() if v is not None}

        logger.info(
            "JSON Payload for the Slice Manager: "
            f"{json.dumps(payload, indent=4)}"
        )

        return payload


    def _process_init(
        self, namespace: str, name: str
        ) -> None:

        patch = {
            "spec": {
                "status": "RUNNING"
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
                f"Updated 'spec.status' for {name} in "
                f"{namespace} to RUNNING")

        except client.exceptions.ApiException as e:
            logger.error(
                "Exception when updating 'spec.status' "
                f"in custom resource: {e}")
            
    def _process_results_update(self, namespace, name, spec, result, operation):
        
        # Get Current Results
        current_results = []
        try:
            current_results = json.loads(
                self.results_cache[f"{namespace}/{name}"]
            )
        except Exception as exc:
            logger.info(f"Could not load camaraResults JSON. Reason {exc}")

        if operation == "CREATE":
            current_results.append(result)
            
        elif operation == "UPDATE":
            for c_result in current_results:
                if c_result["provisioningId"] == result["provisioningId"]:
                    c_result["status"] = result["status"]
                    c_result["startedAt"] = result["startedAt"]
                    c_result["qosProfile"] = result["qosProfile"]
                    break

        elif operation == "DELETE":
            current_results = [
                r for r
                in current_results
                if r["provisioningId"] != result["provisioningId"]
            ]
    
        logger.info(f"CAMARA Results: {current_results}")
        # Save results in cache
        self.results_cache[f"{namespace}/{name}"] = json.dumps(current_results)
        logger.info(f"Updated Results Cache: {self.results_cache}")
        
        patch = {
            "spec": {
                "qodProv": {
                    "operation": f"{operation}-ALREADY-APPLIED"
                },
                "camaraResults": json.dumps(current_results)
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
                f"Updated 'spec.camaraResults' for {name} in "
                f"{namespace} to RUNNING")

        except client.exceptions.ApiException as e:
            logger.error(
                "Exception when updating 'spec.camaraResults' "
                f"in custom resource: {e}")    


# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr  # noqa: F401
from typing import Any, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.database.base_models.create_provisioning import CreateProvisioning  # noqa: F401
from openapi_server.database.base_models.error_info import ErrorInfo  # noqa: F401
from openapi_server.database.base_models.provisioning_info import ProvisioningInfo  # noqa: F401
from openapi_server.database.base_models.retrieve_provisioning_by_device import RetrieveProvisioningByDevice  # noqa: F401


def test_create_provisioning(client: TestClient):
    """Test case for create_provisioning

    Sets a new provisioning of QoS for a device
    """
    create_provisioning = {"qos_profile":"QCI_1_voice","sink":"https://endpoint.example.com/sink","sink_credential":{"credential_type":"PLAIN"},"device":{"phone_number":"+123456789","ipv6_address":"2001:db8:85a3:8d3:1319:8a2e:370:7344","ipv4_address":{"public_address":"203.0.113.0","public_port":59765},"network_access_identifier":"123456789@domain.com"}}

    headers = {
        "x_correlator": 'x_correlator_example',
        
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/device-qos",
    #    headers=headers,
    #    json=create_provisioning,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_delete_provisioning(client: TestClient):
    """Test case for delete_provisioning

    Deletes a QoD provisioning
    """

    headers = {
        "x_correlator": 'x_correlator_example',
        
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/device-qos/{provisioningId}".format(provisioningId='provisioning_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_provisioning_by_id(client: TestClient):
    """Test case for get_provisioning_by_id

    Get QoD provisioning information
    """

    headers = {
        "x_correlator": 'x_correlator_example',
        
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/device-qos/{provisioningId}".format(provisioningId='provisioning_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_retrieve_provisioning_by_device(client: TestClient):
    """Test case for retrieve_provisioning_by_device

    Gets the QoD provisioning for a device
    """
    retrieve_provisioning_by_device = {"device":{"phone_number":"+123456789","ipv6_address":"2001:db8:85a3:8d3:1319:8a2e:370:7344","ipv4_address":{"public_address":"203.0.113.0","public_port":59765},"network_access_identifier":"123456789@domain.com"}}

    headers = {
        "x_correlator": 'x_correlator_example',
        
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/retrieve-device-qos",
    #    headers=headers,
    #    json=retrieve_provisioning_by_device,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


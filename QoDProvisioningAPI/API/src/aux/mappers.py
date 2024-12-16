# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024

from database.base_models import Provisioning, Device

def map_device_to_dict(device: Device) -> dict:
    return {
        "phone_number": device.phone_number,
        "network_access_identifier": device.network_access_identifier,
        "ipv4_address": {
            "public_address": device.ipv4_public_address,
            "private_address": device.ipv4_private_address,
            "public_port": device.ipv4_public_port
        },
        "ipv6_address": device.ipv6_address
    }

def map_service_characteristics(provisioning, operation):
    characteristics = [
        {
            "name": "qodProv.device.phoneNumber",
            "value": {"value": provisioning.device.phone_number or ""}
        },
        {
            "name": "qodProv.device.networkAccessIdentifier",
            "value": {"value": provisioning.device.network_access_identifier \
                or ""}
        },
        {
            "name": "qodProv.device.ipv4Address.publicAddress",
            "value": {"value": provisioning.device.ipv4_public_address or ""}
        },
        {
            "name": "qodProv.device.ipv4Address.privateAddress",
            "value": {"value": provisioning.device.ipv4_private_address or ""}
        },
        {
            "name": "qodProv.device.ipv4Address.publicPort",
            "value": {"value": provisioning.device.ipv4_public_port or ""}
        },
        {
            "name": "qodProv.device.ipv6Address",
            "value": {"value": provisioning.device.ipv6_address or ""}
        },
        {
            "name": "qodProv.qosProfile",
            "value": {"value": provisioning.qos_profile}
        },
        {
            "name": "qodProv.operation",
            "value": {"value": operation}
        },
        {
            "name": "qodProv.provisioningId",
            "value": {"value": provisioning.id}
        },
        {
            "name": "qodProv.sink",
            "value": {"value": provisioning.sink or ""}
        },
        {
            "name": "qodProv.sinkCredential.credentialType",
            "value": {"value": provisioning.sink_credential or ""}
        }
    ]
    return characteristics
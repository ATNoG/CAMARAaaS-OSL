# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024

"""
    QoD Provisioning API

    The Quality-On-Demand (QoD) Provisioning API offers a programmable interface for developers to request the assignment of a certain QoS Profile to a certain device, indefinitely.  This API sets up the configuration in the network so the requested QoS profile is applied to an specified device, at any time while the provisioning is available. The device traffic will be treated with a certain QoS profile by the network whenever the device is connected to the network, until the provisioning is deleted.   # Relevant terms and definitions  * **QoS profiles and QoS profile labels**: Latency, throughput or priority requirements of the application mapped to relevant QoS profile values. The set of QoS Profiles that a network operator is offering may be retrieved via the `qos-profiles` API (cf. https://github.com/camaraproject/QualityOnDemand/) or will be agreed during the onboarding with the API service provider.  * **Identifier for the device**: At least one identifier for the device (user equipment) out of four options: IPv4 address, IPv6 address, Phone number, or Network Access Identifier assigned by the network operator for the device, at the request time. After the provisioning request is accepted, the device may get different IP addresses, but the provisioning will still apply to the device that was identified during the request process. Note: Network Access Identifier is defined for future use and will not be supported with v0.1 of the API.  * **Notification URL and token**: Developers may provide a callback URL (`sink`) on which notifications about all status change events (eg. provisioning termination) can be received from the service provider. This is an optional parameter. The notification will be sent as a CloudEvent compliant message. If `sink` is included, it is RECOMMENDED for the client to provide as well the `sinkCredential` property to protect the notification endpoint. In the current version,`sinkCredential.credentialType` MUST be set to `ACCESSTOKEN` if provided.  # Resources and Operations overview The API defines four operations:  - An operation to setup a new QoD provisioning for a given device. - An operation to get the information about a specific QoD provisioning, identified by its `provisioningId`. - An operation to get the QoD provisioning for a given device. - An operation to terminate a QoD provisioning, identified by its `provisioningId`.  # Authorization and Authentication  [Camara Security and Interoperability Profile](https://github.com/camaraproject/IdentityAndConsentManagement/blob/main/documentation/CAMARA-Security-Interoperability.md) provides details on how a client requests an access token.  Which specific authorization flows are to be used will be determined during onboarding process, happening between the API Client and the Telco Operator exposing the API, taking into account the declared purpose for accessing the API, while also being subject to the prevailing legal framework dictated by local legislation.  It is important to remark that in cases where personal user data is processed by the API, and users can exercise their rights through mechanisms such as opt-in and/or opt-out, the use of 3-legged access tokens becomes mandatory. This measure ensures that the API remains in strict compliance with user privacy preferences and regulatory obligations, upholding the principles of transparency and user-centric data control.  # Identifying a device from the access token  This specification defines the `device` object field as optional in API requests, specifically in cases where the API is accessed using a 3-legged access token, and the device can be uniquely identified by the token. This approach simplifies API usage for API consumers by relying on the device information associated with the access token used to invoke the API.  ## Handling of device information:  ### Optional device object for 3-legged tokens:  - When using a 3-legged access token, the device associated with the access token must be considered as the device for the API request. This means that the device object is not required in the request, and if included it must identify the same device, therefore **it is recommended NOT to include it in these scenarios** to simplify the API usage and avoid additional validations.  ### Validation mechanism:  - The server will extract the device identification from the access token, if available. - If the API request additionally includes a `device` object when using a 3-legged access token, the API will validate that the device identifier provided matches the one associated with the access token. - If there is a mismatch, the API will respond with a 403 - INVALID_TOKEN_CONTEXT error, indicating that the device information in the request does not match the token.  ### Error handling for unidentifiable devices:  - If the `device` object is not included in the request and the device information cannot be derived from the 3-legged access token, the server will return a 422 `UNIDENTIFIABLE_DEVICE` error.  ### Restrictions for tokens without an associated authenticated identifier:  - For scenarios which do not have a single device identifier associated to the token during the authentication flow, e.g. 2-legged access tokens, the `device` object MUST be provided in the API request. This ensures that the device identification is explicit and valid for each API call made with these tokens. 

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import asyncio
import json

from fastapi import FastAPI
from sqlalchemy.orm import Session

from routers.qod_provisioning_router import router as QoDProvisioningApiRouter
from routers.osl import router as OSLRouter

from database.db import init_db, get_db
from aux.service_event_manager.service_event_manager import ServiceEventManager
from aux.service_event_manager.camara_results_processor import CamaraResultsProcessor
from config import Config

# Set up logging
logger = Config.setup_logging()

app = FastAPI(
    title="QoD Provisioning API",
    description=(
    "The Quality-On-Demand (QoD) Provisioning API offers a programmable "
    "interface for developers to request the assignment of a certain QoS "
    "Profile to a certain device, indefinitely.\n\n"
    
    "This API sets up the configuration in the network so the requested QoS profile is applied to a specified device, at any time while the provisioning is available. The device traffic will be treated with a certain QoS profile by the network whenever the device is connected to the network, until the provisioning is deleted.\n\n"

    "## Relevant terms and definitions\n\n"

    "* **QoS profiles and QoS profile labels**: Latency, throughput or priority requirements of the application mapped to relevant QoS profile values. The set of QoS Profiles that a network operator is offering may be retrieved via the `qos-profiles` API (cf. https://github.com/camaraproject/QualityOnDemand/) or will be agreed during the onboarding with the API service provider.\n\n"

    "* **Identifier for the device**: At least one identifier for the device (user equipment) out of four options: IPv4 address, IPv6 address, Phone number, or Network Access Identifier assigned by the network operator for the device, at the request time. After the provisioning request is accepted, the device may get different IP addresses, but the provisioning will still apply to the device that was identified during the request process. Note: Network Access Identifier is defined for future use and will not be supported with v0.1 of the API.\n\n"

    "* **Notification URL and token**: Developers may provide a callback URL (`sink`) on which notifications about all status change events (eg. provisioning termination) can be received from the service provider. This is an optional parameter. The notification will be sent as a CloudEvent compliant message. If `sink` is included, it is RECOMMENDED for the client to provide as well the `sinkCredential` property to protect the notification endpoint. In the current version, `sinkCredential.credentialType` MUST be set to `ACCESSTOKEN` if provided.\n\n"

    "## Resources and Operations overview\n\n"

    "The API defines four operations:\n\n"

    "- An operation to setup a new QoD provisioning for a given device.\n\n"
    "- An operation to get the information about a specific QoD provisioning, identified by its `provisioningId`.\n\n"
    "- An operation to get the QoD provisioning for a given device.\n\n"
    "- An operation to terminate a QoD provisioning, identified by its `provisioningId`.\n\n"

    "## Authorization and Authentication\n\n"

    "[Camara Security and Interoperability Profile](https://github.com/camaraproject/IdentityAndConsentManagement/blob/main/documentation/CAMARA-Security-Interoperability.md) provides details on how a client requests an access token.\n\n"

    "Which specific authorization flows are to be used will be determined during onboarding process, happening between the API Client and the Telco Operator exposing the API, taking into account the declared purpose for accessing the API, while also being subject to the prevailing legal framework dictated by local legislation. It is important to remark that in cases where personal user data is processed by the API, and users can exercise their rights through mechanisms such as opt-in and/or opt-out, the use of 3-legged access tokens becomes mandatory. This measure ensures that the API remains in strict compliance with user privacy preferences and regulatory obligations, upholding the principles of transparency and user-centric data control.\n\n"

    "## Identifying a device from the access token\n\n"

    "This specification defines the `device` object field as optional in API requests, specifically in cases where the API is accessed using a 3-legged access token, and the device can be uniquely identified by the token. This approach simplifies API usage for API consumers by relying on the device information associated with the access token used to invoke the API.\n\n"

    "### Handling of device information:\n\n"

    "#### Optional device object for 3-legged tokens:\n\n"

    "- When using a 3-legged access token, the device associated with the access token must be considered as the device for the API request. This means that the device object is not required in the request, and if included it must identify the same device, therefore **it is recommended NOT to include it in these scenarios** to simplify the API usage and avoid additional validations.\n\n"

    "#### Validation mechanism:\n\n"

    "- The server will extract the device identification from the access token, if available.\n\n"
    "- If the API request additionally includes a `device` object when using a 3-legged access token, the API will validate that the device identifier provided matches the one associated with the access token.\n\n"
    "- If there is a mismatch, the API will respond with a 403 - INVALID_TOKEN_CONTEXT error, indicating that the device information in the request does not match the token.\n\n"

    "#### Error handling for unidentifiable devices:\n\n"

    "- If the `device` object is not included in the request and the device information cannot be derived from the 3-legged access token, the server will return a 422 `UNIDENTIFIABLE_DEVICE` error.\n\n"

    "#### Restrictions for tokens without an associated authenticated identifier:\n\n"

    "- For scenarios which do not have a single device identifier associated to the token during the authentication flow, e.g. 2-legged access tokens, the `device` object MUST be provided in the API request. This ensures that the device identification is explicit and valid for each API call made with these tokens.\n\n"
    ),
    version="0.1.0",
)

app.include_router(QoDProvisioningApiRouter)
app.include_router(OSLRouter)

@app.on_event("startup")
async def startup_event():
    """
    Event triggered when the application starts.
    Initializes the database tables.
    """
    init_db()

    # Initialize the ServiceEventManager and subscribe to OSL events topic
    ServiceEventManager.initialize()
    ServiceEventManager.subscribe_to_events()

    # Initialize the CamaraResultsProcessor with the queue and start processing
    camara_processor = CamaraResultsProcessor(
        ServiceEventManager.camara_results_queue
    )
    asyncio.create_task(camara_processor.process_results())

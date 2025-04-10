# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 10:13:05
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-11-28 17:07:23
# coding: utf-8

"""
    QoD Provisioning API

    The Quality-On-Demand (QoD) Provisioning API offers a programmable interface for developers to request the assignment of a certain QoS Profile to a certain device, indefinitely.  This API sets up the configuration in the network so the requested QoS profile is applied to an specified device, at any time while the provisioning is available. The device traffic will be treated with a certain QoS profile by the network whenever the device is connected to the network, until the provisioning is deleted.   # Relevant terms and definitions  * **QoS profiles and QoS profile labels**: Latency, throughput or priority requirements of the application mapped to relevant QoS profile values. The set of QoS Profiles that a network operator is offering may be retrieved via the `qos-profiles` API (cf. https://github.com/camaraproject/QualityOnDemand/) or will be agreed during the onboarding with the API service provider.  * **Identifier for the device**: At least one identifier for the device (user equipment) out of four options: IPv4 address, IPv6 address, Phone number, or Network Access Identifier assigned by the network operator for the device, at the request time. After the provisioning request is accepted, the device may get different IP addresses, but the provisioning will still apply to the device that was identified during the request process. Note: Network Access Identifier is defined for future use and will not be supported with v0.1 of the API.  * **Notification URL and token**: Developers may provide a callback URL (`sink`) on which notifications about all status change events (eg. provisioning termination) can be received from the service provider. This is an optional parameter. The notification will be sent as a CloudEvent compliant message. If `sink` is included, it is RECOMMENDED for the client to provide as well the `sinkCredential` property to protect the notification endpoint. In the current version,`sinkCredential.credentialType` MUST be set to `ACCESSTOKEN` if provided.  # Resources and Operations overview The API defines four operations:  - An operation to setup a new QoD provisioning for a given device. - An operation to get the information about a specific QoD provisioning, identified by its `provisioningId`. - An operation to get the QoD provisioning for a given device. - An operation to terminate a QoD provisioning, identified by its `provisioningId`.  # Authorization and Authentication  [Camara Security and Interoperability Profile](https://github.com/camaraproject/IdentityAndConsentManagement/blob/main/documentation/CAMARA-Security-Interoperability.md) provides details on how a client requests an access token.  Which specific authorization flows are to be used will be determined during onboarding process, happening between the API Client and the Telco Operator exposing the API, taking into account the declared purpose for accessing the API, while also being subject to the prevailing legal framework dictated by local legislation.  It is important to remark that in cases where personal user data is processed by the API, and users can exercise their rights through mechanisms such as opt-in and/or opt-out, the use of 3-legged access tokens becomes mandatory. This measure ensures that the API remains in strict compliance with user privacy preferences and regulatory obligations, upholding the principles of transparency and user-centric data control.  # Identifying a device from the access token  This specification defines the `device` object field as optional in API requests, specifically in cases where the API is accessed using a 3-legged access token, and the device can be uniquely identified by the token. This approach simplifies API usage for API consumers by relying on the device information associated with the access token used to invoke the API.  ## Handling of device information:  ### Optional device object for 3-legged tokens:  - When using a 3-legged access token, the device associated with the access token must be considered as the device for the API request. This means that the device object is not required in the request, and if included it must identify the same device, therefore **it is recommended NOT to include it in these scenarios** to simplify the API usage and avoid additional validations.  ### Validation mechanism:  - The server will extract the device identification from the access token, if available. - If the API request additionally includes a `device` object when using a 3-legged access token, the API will validate that the device identifier provided matches the one associated with the access token. - If there is a mismatch, the API will respond with a 403 - INVALID_TOKEN_CONTEXT error, indicating that the device information in the request does not match the token.  ### Error handling for unidentifiable devices:  - If the `device` object is not included in the request and the device information cannot be derived from the 3-legged access token, the server will return a 422 `UNIDENTIFIABLE_DEVICE` error.  ### Restrictions for tokens without an associated authenticated identifier:  - For scenarios which do not have a single device identifier associated to the token during the authentication flow, e.g. 2-legged access tokens, the `device` object MUST be provided in the API request. This ensures that the device identification is explicit and valid for each API call made with these tokens. 

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json




from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from typing_extensions import Annotated
from schemas.device import Device
from schemas.sink_credential import SinkCredential
from schemas.status import Status
from schemas.status_info import StatusInfo
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ProvisioningInfo(BaseModel):
    """
    Provisioning related information returned in responses. Optional device object only to be returned if provided in createProvisioning. If more than one type of device identifier was provided, only one identifier will be returned (at implementation choice and with the original value provided in createProvisioning). Please note that IP addresses of devices can change and get reused, so the original values may no longer identify the same device. They identified the device at the time of QoD provisioning creation. 
    """ # noqa: E501
    device: Optional[Device] = None
    qos_profile: Annotated[str, Field(min_length=3, strict=True, max_length=256)] = Field(description="A unique name for identifying a specific QoS profile. This may follow different formats depending on the service providers implementation. Some options addresses:   - A UUID style string   - Support for predefined profiles QOS_S, QOS_M, QOS_L, and QOS_E   - A searchable descriptive name The set of QoS Profiles that an operator is offering can be retrieved by means of the [QoS Profile API](link TBC). ", alias="qosProfile")
    sink: Optional[StrictStr] = Field(default=None, description="The address to which events shall be delivered, using the HTTP protocol.")
    sink_credential: Optional[SinkCredential] = Field(default=None, alias="sinkCredential")
    provisioning_id: StrictStr = Field(description="Provisioning Identifier in UUID format", alias="provisioningId")
    started_at: Optional[datetime] = Field(default=None, description="Date and time when the provisioning became \"AVAILABLE\". Not to be returned when `status` is \"REQUESTED\". Format must follow RFC 3339 and must indicate time zone (UTC or local).", alias="startedAt")
    status: Status
    status_info: Optional[StatusInfo] = Field(default=None, alias="statusInfo")
    __properties: ClassVar[List[str]] = ["device", "qosProfile", "sink", "sinkCredential", "provisioningId", "startedAt", "status", "statusInfo"]

    @field_validator('qos_profile')
    def qos_profile_validate_regular_expression(cls, value):
        """Validates the regular expression"""
        if not re.match(r"^[a-zA-Z0-9_.-]+$", value):
            raise ValueError(r"must validate the regular expression /^[a-zA-Z0-9_.-]+$/")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of ProvisioningInfo from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of device
        if self.device:
            _dict['device'] = self.device.to_dict()
        # override the default output from pydantic by calling `to_dict()` of sink_credential
        if self.sink_credential:
            _dict['sinkCredential'] = self.sink_credential.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of ProvisioningInfo from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "device": Device.from_dict(obj.get("device")) if obj.get("device") is not None else None,
            "qosProfile": obj.get("qosProfile"),
            "sink": obj.get("sink"),
            "sinkCredential": SinkCredential.from_dict(obj.get("sinkCredential")) if obj.get("sinkCredential") is not None else None,
            "provisioningId": obj.get("provisioningId"),
            "startedAt": obj.get("startedAt"),
            "status": obj.get("status"),
            "statusInfo": obj.get("statusInfo")
        })
        return _obj



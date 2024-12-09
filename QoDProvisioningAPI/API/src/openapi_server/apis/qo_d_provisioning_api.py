# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 10:13:05
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-11-29 12:31:44
# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.qo_d_provisioning_api_base import BaseQoDProvisioningApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.database.schemas.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from openapi_server.database.db import get_db
from fastapi import HTTPException, Depends
from openapi_server.database.schemas.create_provisioning import CreateProvisioning
from openapi_server.database.schemas.error_info import ErrorInfo
from openapi_server.database.schemas.provisioning_info import ProvisioningInfo
from openapi_server.database.schemas.retrieve_provisioning_by_device import RetrieveProvisioningByDevice
from openapi_server.database import crud
#from openapi_server.security_api import get_token_openId

import logging

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/device-qos",
    responses={
        201: {"model": ProvisioningInfo, "description": "Provisioning created"},
        400: {"model": ErrorInfo, "description": "Bad Request with additional errors for implicit notifications"},
        401: {"model": ErrorInfo, "description": "Unauthorized"},
        403: {"model": ErrorInfo, "description": "Forbidden"},
        404: {"model": ErrorInfo, "description": "Not found"},
        409: {"model": ErrorInfo, "description": "Provisioning conflict"},
        422: {"model": ErrorInfo, "description": "Unprocessable entity"},
        429: {"model": ErrorInfo, "description": "Too Many Requests"},
        500: {"model": ErrorInfo, "description": "Internal server error"},
        503: {"model": ErrorInfo, "description": "Service unavailable"},
    },
    tags=["QoD Provisioning"],
    summary="Sets a new provisioning of QoS for a device",
    response_model_by_alias=True,
    status_code=201  # Default status code for successful creation
)
async def create_provisioning(
    create_provisioning: Annotated[CreateProvisioning, Field(description="Parameters to create a new provisioning")] = Body(None, description="Parameters to create a new provisioning"),
    x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")] = Header(None, description="Correlation id for the different services"),
    db_session: Session = Depends(get_db)
    #token_openId: TokenModel = Security(
    #    get_token_openId
    #),
) -> ProvisioningInfo:
    """Triggers a new provisioning in the operator to assign certain QoS Profile to certain device.  - If the provisioning is completed synchronously, the response will be 201 with &#x60;status&#x60; &#x3D; &#x60;AVAILABLE&#x60;. - If the provisioning request is accepted but not yet completed, the response will be 201 with &#x60;status&#x60; &#x3D; &#x60;REQUESTED&#x60;. - If the operator determines synchronously that the provisioning request cannot be fulfilled, the response will be 201 with &#x60;status&#x60; &#x3D; &#x60;UNAVAILABLE&#x60;.  - If the request includes  the &#x60;sink&#x60; and &#x60;sinkCredential&#x60; properties, the client will receive a &#x60;status-changed&#x60; event with the outcome of the process. The event will be sent also for synchronous operations.  **NOTES:** - When the provisioning status becomes &#x60;UNAVAILABLE&#x60;, the QoD provisioning resource is not immediately released, but will get deleted automatically, at earliest 360 seconds after.  This behavior allows clients which are not receiving notification events but are polling, to get the provisioning status information. Before a client can attempt to create a new QoD provisioning for the same device, they must release the provisioning resources with an explicit &#x60;delete&#x60; operation if not yet automatically deleted. - The access token may be either 2-legged or 3-legged.   - If a 3-legged access token which is associated with a device is used, it is recommended NOT to include the &#x60;device&#x60; parameter in the request (see \&quot;Handling of device information\&quot; within the API description for details).   - If a 2-legged access token is used, the device parameter must be provided and identify a device. """
    
    if not BaseQoDProvisioningApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    
    return await BaseQoDProvisioningApi.subclasses[0]().create_provisioning(create_provisioning, x_correlator, db_session)


@router.delete(
    "/device-qos/{provisioningId}",
    responses={
        204: {"description": "Provisioning deleted"},
        202: {"model": ProvisioningInfo, "description": "Deletion request accepted to be processed. It applies for an async deletion process. &#x60;status&#x60; in the response will be &#x60;AVAILABLE&#x60; with &#x60;statusInfo&#x60; set to &#x60;DELETE_REQUESTED&#x60;."},
        400: {"model": ErrorInfo, "description": "Bad Request"},
        401: {"model": ErrorInfo, "description": "Unauthorized"},
        403: {"model": ErrorInfo, "description": "Forbidden"},
        404: {"model": ErrorInfo, "description": "Not found"},
        429: {"model": ErrorInfo, "description": "Too Many Requests"},
        500: {"model": ErrorInfo, "description": "Internal server error"},
        503: {"model": ErrorInfo, "description": "Service unavailable"},
    },
    tags=["QoD Provisioning"],
    summary="Deletes a QoD provisioning",
    response_model_by_alias=True,
)
async def delete_provisioning(
    provisioningId: Annotated[StrictStr, Field(description="Provisioning ID that was obtained from the createProvision operation")] = Path(..., description="Provisioning ID that was obtained from the createProvision operation"),
    x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")] = Header(None, description="Correlation id for the different services"),
    db_session: Session = Depends(get_db)
    #token_openId: TokenModel = Security(
    #    get_token_openId
    #),
) -> ProvisioningInfo:
    """Release resources related to QoS provisioning.  If the notification callback is provided and the provisioning status was &#x60;AVAILABLE&#x60;, when the deletion is completed, the client will receive in addition to the response a &#x60;PROVISIONING_STATUS_CHANGED&#x60; event with - &#x60;status&#x60; as &#x60;UNAVAILABLE&#x60; and - &#x60;statusInfo&#x60; as &#x60;DELETE_REQUESTED&#x60; There will be no notification event if the &#x60;status&#x60; was already &#x60;UNAVAILABLE&#x60;.  **NOTES:** - The access token may be either 2-legged or 3-legged. - If a 3-legged access token is used, the end user (and device) associated with the QoD provisioning must also be associated with the access token. - The QoD provisioning must have been created by the same API client given in the access token. """
    if not BaseQoDProvisioningApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")

    return await BaseQoDProvisioningApi.subclasses[0]().delete_provisioning(provisioningId, x_correlator, db_session)


@router.get(
    "/device-qos/{provisioningId}",
    responses={
        200: {"model": ProvisioningInfo, "description": "Returns information about certain provisioning"},
        400: {"model": ErrorInfo, "description": "Bad Request"},
        401: {"model": ErrorInfo, "description": "Unauthorized"},
        403: {"model": ErrorInfo, "description": "Forbidden"},
        404: {"model": ErrorInfo, "description": "Not found"},
        429: {"model": ErrorInfo, "description": "Too Many Requests"},
        500: {"model": ErrorInfo, "description": "Internal server error"},
        503: {"model": ErrorInfo, "description": "Service unavailable"},
    },
    tags=["QoD Provisioning"],
    summary="Get QoD provisioning information",
    response_model_by_alias=True,
)
async def get_provisioning_by_id(
    provisioningId: Annotated[StrictStr, Field(description="Provisioning ID that was obtained from the createProvision operation")] = Path(..., description="Provisioning ID that was obtained from the createProvision operation"),
    x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")] = Header(None, description="Correlation id for the different services"),
    db_session: Session = Depends(get_db)
    #token_openId: TokenModel = Security(
    #    get_token_openId
    #),
) -> ProvisioningInfo:
    """Querying for QoD provisioning resource information details  **NOTES:** - The access token may be either 2-legged or 3-legged. - If a 3-legged access token is used, the end user (and device) associated with the QoD provisioning must also be associated with the access token. - The QoD provisioning must have been created by the same API client given in the access token. """
    if not BaseQoDProvisioningApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")

    return await BaseQoDProvisioningApi.subclasses[0]().get_provisioning_by_id(provisioningId, x_correlator, db_session)


@router.post(
    "/retrieve-device-qos",
    responses={
        200: {"model": ProvisioningInfo, "description": "Returns information about QoS provisioning for the device."},
        400: {"model": ErrorInfo, "description": "Bad Request"},
        401: {"model": ErrorInfo, "description": "Unauthorized"},
        403: {"model": ErrorInfo, "description": "Forbidden"},
        404: {"model": ErrorInfo, "description": "Not found"},
        422: {"model": ErrorInfo, "description": "Unprocessable entity"},
        429: {"model": ErrorInfo, "description": "Too Many Requests"},
        500: {"model": ErrorInfo, "description": "Internal server error"},
        503: {"model": ErrorInfo, "description": "Service unavailable"},
    },
    tags=["QoD Provisioning"],
    summary="Gets the QoD provisioning for a device",
    response_model_by_alias=True,
)
async def retrieve_provisioning_by_device(
    retrieve_provisioning_by_device: Annotated[RetrieveProvisioningByDevice, Field(description="Parameters to retrieve a provisioning by device")] = Body(None, description="Parameters to retrieve a provisioning by device"),
    x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")] = Header(None, description="Correlation id for the different services"),
    db_session: Session = Depends(get_db)
    #token_openId: TokenModel = Security(
    #    get_token_openId
    #),
) -> ProvisioningInfo:
    """Retrieves the QoD provisioning for a device.  **NOTES:** - The access token may be either 2-legged or 3-legged.   - If a 3-legged access token is used, the end user (and device) associated with the QoD provisioning must also be associated with the access token. In this case it is recommended NOT to include the &#x60;device&#x60; parameter in the request (see \&quot;Handling of device information\&quot; within the API description for details).   - If a 2-legged access token is used, the device parameter must be provided and identify a device. - The QoD provisioning must have been created by the same API client given in the access token. - If no provisioning is found for the device, an error response 404 is returned with code \&quot;NOT_FOUND\&quot;. """
    if not BaseQoDProvisioningApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
        
    return await BaseQoDProvisioningApi.subclasses[0]().retrieve_provisioning_by_device(retrieve_provisioning_by_device, x_correlator, db_session)

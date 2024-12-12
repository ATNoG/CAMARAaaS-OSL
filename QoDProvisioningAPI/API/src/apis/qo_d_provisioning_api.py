# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 10:13:05
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-11-29 12:31:44
# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from apis.qo_d_provisioning_api_base import BaseQoDProvisioningApi

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

from schemas.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from database.db import get_db
from fastapi import HTTPException, Depends
from schemas.create_provisioning import CreateProvisioning
from schemas.error_info import ErrorInfo
from schemas.provisioning_info import ProvisioningInfo
from schemas.retrieve_provisioning_by_device import RetrieveProvisioningByDevice
from database import crud
from aux import mappers
from datetime import datetime
import logging
from aux.service_event_manager.service_event_manager import ServiceEventManager
import json

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()


@router.post(
    "/device-qos",
    responses={
        201: {"model": ProvisioningInfo, "description": "Provisioning created"},
        400: {"model": ErrorInfo, "description": 
        "Bad Request with additional errors for implicit notifications"},
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
    create_provisioning: CreateProvisioning,
    x_correlator: Annotated[
        Optional[StrictStr],
        Field(description="Correlation id for the different services")
    ] = Header(None, description="Correlation id for the different services"),
    db_session: Session = Depends(get_db)
) -> ProvisioningInfo:
    try:
        # Call the CRUD function to create the provisioning in the database
        new_provisioning = crud.create_provisioning(
            db_session,
            create_provisioning
        )
        
        print("HELLO", new_provisioning.device.ipv4_private_address)
        ServiceEventManager.update_service(
                {   
                    # TODO: CREATE FUNCTION TO MAP THIS
                    "serviceCharacteristic": [
                        {
                            "name": "qodProv.device.phoneNumber",
                            "value":{
                                "value": new_provisioning.device.phone_number \
                                if  new_provisioning.device.phone_number
                                else ""
                            }
                        },
                        {"name": "qodProv.device.networkAccessIdentifier",
                         "value": {"value": new_provisioning.device.network_access_identifier}
                        },
                        {"name": "qodProv.device.ipv4Address.publicAddress",
                         "value": {"value": new_provisioning.device.ipv4_public_address}
                        },
                        {
                            "name": "qodProv.device.ipv4Address.privateAddress",
                            "value":{
                                "value": new_provisioning.device.ipv4_private_address \
                                if  new_provisioning.device.ipv4_private_address
                                else ""
                            }
                        },
                        # TODO: Change this -> public port
                        {"name": "qodProv.device.ipv4Address.privatePort",
                         "value": {"value": new_provisioning.device.ipv4_public_port}
                        },
                        {"name": "qodProv.qosProfile",
                         "value": {"value": new_provisioning.qos_profile}
                        },
                        # Todo: Create Sink Info on target Svc Characteristics
                        {"name": "qodProv.operation",
                         "value": {"value": "CREATE"}
                        },
                        {"name": "qodProv.provisioningId",
                         "value": {"value": new_provisioning.id}
                        }                        
                    ]
                }
        )
        
        
        return ProvisioningInfo(
            provisioning_id=new_provisioning.id,
            device=mappers.map_device_to_dict(new_provisioning.device),
            qos_profile=new_provisioning.qos_profile,
            sink=new_provisioning.sink,
            sink_credential={
                "credential_type": new_provisioning.sink_credential
            },
            started_at=datetime.utcnow(),
            status=new_provisioning.status,
            status_info=new_provisioning.status_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # If an error occurs, roll back and raise an HTTPException
        raise HTTPException(status_code=500, detail=str(e))
        
    #if not BaseQoDProvisioningApi.subclasses:
    #    raise HTTPException(status_code=500, detail="Not implemented")
    
    #return await BaseQoDProvisioningApi.subclasses[0]().create_provisioning(create_provisioning, x_correlator, db_session)


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

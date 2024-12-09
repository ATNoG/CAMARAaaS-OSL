# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 10:13:05
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-12-09 11:15:18
# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from openapi_server.database.db import get_db
from openapi_server.database import crud
from openapi_server.database.schemas.create_provisioning import CreateProvisioning
from openapi_server.database.schemas.error_info import ErrorInfo
from openapi_server.database.schemas.provisioning_info import ProvisioningInfo
from openapi_server.database.schemas.retrieve_provisioning_by_device import RetrieveProvisioningByDevice
#from openapi_server.security_api import get_token_openId

import logging

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BaseQoDProvisioningApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseQoDProvisioningApi.subclasses = BaseQoDProvisioningApi.subclasses + (cls,)
    async def create_provisioning(
        self,
        create_provisioning: Annotated[CreateProvisioning, Field(description="Parameters to create a new provisioning")],
        x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")],
        db_session: Session = Depends(get_db)
    ) -> ProvisioningInfo:
        """Triggers a new provisioning in the operator to assign certain QoS Profile to certain device.  - If the provisioning is completed synchronously, the response will be 201 with &#x60;status&#x60; &#x3D; &#x60;AVAILABLE&#x60;. - If the provisioning request is accepted but not yet completed, the response will be 201 with &#x60;status&#x60; &#x3D; &#x60;REQUESTED&#x60;. - If the operator determines synchronously that the provisioning request cannot be fulfilled, the response will be 201 with &#x60;status&#x60; &#x3D; &#x60;UNAVAILABLE&#x60;.  - If the request includes  the &#x60;sink&#x60; and &#x60;sinkCredential&#x60; properties, the client will receive a &#x60;status-changed&#x60; event with the outcome of the process. The event will be sent also for synchronous operations.  **NOTES:** - When the provisioning status becomes &#x60;UNAVAILABLE&#x60;, the QoD provisioning resource is not immediately released, but will get deleted automatically, at earliest 360 seconds after.  This behavior allows clients which are not receiving notification events but are polling, to get the provisioning status information. Before a client can attempt to create a new QoD provisioning for the same device, they must release the provisioning resources with an explicit &#x60;delete&#x60; operation if not yet automatically deleted. - The access token may be either 2-legged or 3-legged.   - If a 3-legged access token which is associated with a device is used, it is recommended NOT to include the &#x60;device&#x60; parameter in the request (see \&quot;Handling of device information\&quot; within the API description for details).   - If a 2-legged access token is used, the device parameter must be provided and identify a device. """

        try:
            # Call the CRUD function to create the provisioning in the database
            new_provisioning = crud.create_provisioning(db_session, create_provisioning)

            return new_provisioning

        except HTTPException:
            # Allow 404 and other HTTPExceptions to propagate without modification
            raise

        except Exception as e:
            # If an error occurs, roll back and raise an HTTPException
            raise HTTPException(status_code=500, detail=str(e))


    async def delete_provisioning(
        self,
        provisioningId: Annotated[StrictStr, Field(description="Provisioning ID that was obtained from the createProvision operation")],
        x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")],
        db_session: Session = Depends(get_db)
    ) -> ProvisioningInfo:
        """Release resources related to QoS provisioning.  If the notification callback is provided and the provisioning status was &#x60;AVAILABLE&#x60;, when the deletion is completed, the client will receive in addition to the response a &#x60;PROVISIONING_STATUS_CHANGED&#x60; event with - &#x60;status&#x60; as &#x60;UNAVAILABLE&#x60; and - &#x60;statusInfo&#x60; as &#x60;DELETE_REQUESTED&#x60; There will be no notification event if the &#x60;status&#x60; was already &#x60;UNAVAILABLE&#x60;.  **NOTES:** - The access token may be either 2-legged or 3-legged. - If a 3-legged access token is used, the end user (and device) associated with the QoD provisioning must also be associated with the access token. - The QoD provisioning must have been created by the same API client given in the access token. """
        try:
            # Call the CRUD function to create the provisioning in the database
            deleted_provisioning = crud.delete_provisioning(db_session, provisioningId)

            return deleted_provisioning
        
        except HTTPException:
            # Allow 404 and other HTTPExceptions to propagate without modification
            raise

        except Exception as e:
            # If an error occurs, roll back and raise an HTTPException
            raise HTTPException(status_code=500, detail=str(e))


    async def get_provisioning_by_id(
        self,
        provisioningId: Annotated[StrictStr, Field(description="Provisioning ID that was obtained from the createProvision operation")],
        x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")],
        db_session: Session = Depends(get_db)
    ) -> ProvisioningInfo:
        """Querying for QoD provisioning resource information details  **NOTES:** - The access token may be either 2-legged or 3-legged. - If a 3-legged access token is used, the end user (and device) associated with the QoD provisioning must also be associated with the access token. - The QoD provisioning must have been created by the same API client given in the access token. """
        try:
            # Call the CRUD function to create the provisioning in the database
            provisioning = crud.get_provisioning_by_id(db_session, provisioningId)

            return provisioning
        
        except HTTPException:
            # Allow 404 and other HTTPExceptions to propagate without modification
            raise
        
        except Exception as e:
            # If an error occurs, roll back and raise an HTTPException
            raise HTTPException(status_code=500, detail=str(e))


    async def retrieve_provisioning_by_device(
        self,
        retrieve_provisioning_by_device: Annotated[RetrieveProvisioningByDevice, Field(description="Parameters to retrieve a provisioning by device")],
        x_correlator: Annotated[Optional[StrictStr], Field(description="Correlation id for the different services")],
        db_session: Session = Depends(get_db)
    ) -> ProvisioningInfo:
        """Retrieves the QoD provisioning for a device.  **NOTES:** - The access token may be either 2-legged or 3-legged.   - If a 3-legged access token is used, the end user (and device) associated with the QoD provisioning must also be associated with the access token. In this case it is recommended NOT to include the &#x60;device&#x60; parameter in the request (see \&quot;Handling of device information\&quot; within the API description for details).   - If a 2-legged access token is used, the device parameter must be provided and identify a device. - The QoD provisioning must have been created by the same API client given in the access token. - If no provisioning is found for the device, an error response 404 is returned with code \&quot;NOT_FOUND\&quot;. """
        try:
            # Call the CRUD function to create the provisioning in the database
            provisioning = crud.get_provisioning_by_device(db_session, retrieve_provisioning_by_device)

            return provisioning

        except HTTPException:
            # Allow 404 and other HTTPExceptions to propagate without modification
            raise

        except Exception as e:
            # If an error occurs, roll back and raise an HTTPException
            raise HTTPException(status_code=500, detail=str(e))

# Concrete subclass that should be used in your API
class QoDProvisioningImpl(BaseQoDProvisioningApi):
    pass
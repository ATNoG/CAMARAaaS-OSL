# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 10:13:05
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-11-29 12:31:44
# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

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
from schemas.status import Status
from schemas.status_info import StatusInfo
from database import crud
from aux import mappers
from datetime import datetime
import logging
from aux.service_event_manager.service_event_manager import ServiceEventManager
import json
from config import Config
from aux.constants import Constants
# Set up logging
logger = Config.setup_logging()

router = APIRouter()


@router.get(
    "/osl/current-camara-results",
    tags=["OSL"],
    summary=(
        "This endpoint is only used when this service is deployed "
        "with OSL. It is used to get a list of the camaraResults "
        "processed by the API"
    ),
    response_model_by_alias=True,
    status_code=200
)
async def current_camara_results() -> List[ProvisioningInfo]:
    return Constants.processed_camara_results
        

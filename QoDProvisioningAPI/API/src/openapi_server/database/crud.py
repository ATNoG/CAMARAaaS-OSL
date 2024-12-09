# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 15:03:52
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-12-09 14:37:49

from sqlalchemy.orm import Session
from openapi_server.database.db import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from fastapi import HTTPException

from openapi_server.database.schemas.create_provisioning import CreateProvisioning
from openapi_server.database.base_models import *
from openapi_server.database.schemas.provisioning_info import ProvisioningInfo
from openapi_server.database.schemas.status import Status
from openapi_server.database.schemas.status_changed import StatusChanged
from openapi_server.database.schemas.status_info import StatusInfo
from openapi_server.database.schemas.retrieve_provisioning_by_device import RetrieveProvisioningByDevice


import logging

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Helper Function
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


def create_provisioning(db: Session, create_provisioning: CreateProvisioning) -> ProvisioningInfo:
    """
    Creates a new provisioning in the database.

    Args:
        db: Database session.
        create_provisioning: The data needed to create the provisioning.

    Returns:
        The created ProvisioningInfo object.
    """
    try:
        logger.debug(f"Received provisioning data: {create_provisioning}\n")

        # Check if the device already exists
        existing_device = db.query(Device).filter_by(phone_number=create_provisioning.device.phone_number).first()

        if existing_device:
            logger.debug(f"Device with phone number {create_provisioning.device.phone_number} already exists with ID {existing_device.id}")
            new_device = existing_device
        else:
            # Create a new device instance
            new_device = Device(
                phone_number=create_provisioning.device.phone_number,
                network_access_identifier=create_provisioning.device.network_access_identifier,
                ipv4_public_address=create_provisioning.device.ipv4_address.public_address,
                ipv4_private_address=create_provisioning.device.ipv4_address.private_address,
                ipv4_public_port=create_provisioning.device.ipv4_address.public_port,
                ipv6_address=create_provisioning.device.ipv6_address
            )

            # Add the new device to the session
            db.add(new_device)
            db.commit()
            db.refresh(new_device)

        logger.debug(f"new_device.id: {new_device.id}")

        # Create a new provisioning instance
        new_provisioning = Provisioning(
            qos_profile=create_provisioning.qos_profile,
            sink=create_provisioning.sink,
            device_id=new_device.id,
            sink_credential=create_provisioning.sink_credential.credential_type
        )

        # Add the new provisioning to the session
        db.add(new_provisioning)
        db.commit()
        db.refresh(new_provisioning)

        provisioning_info = ProvisioningInfo(
            provisioning_id=str(new_provisioning.id),
            device=map_device_to_dict(new_device),
            qos_profile=new_provisioning.qos_profile,
            sink=new_provisioning.sink,
            sink_credential={
                "credential_type": new_provisioning.sink_credential
            },
            started_at=datetime.utcnow(),
            status=new_provisioning.status,
            status_info=new_provisioning.status_info
        )
        
        return provisioning_info

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating provisioning: {e}")
        raise ValueError(f"Error creating provisioning: {e}")


def get_provisioning_by_id(db: Session, provisioning_id: str) -> ProvisioningInfo:
    """
    Fetch a provisioning by its ID.

    Args:
        db: Database session.
        provisioning_id: The ID of the provisioning.

    Returns:
        The ProvisioningInfo object or None if not found.
    """
    try:
        logger.debug(f"Received provisioning ID: {provisioning_id}\n")

        # Check if the provisioning exists
        provisioning = db.query(Provisioning).filter_by(id=provisioning_id).first()

        if provisioning:
            if provisioning.status_info:
                provisioning_status_info = provisioning.status_info
            else:
                provisioning_status_info = None

            device = db.query(Device).filter_by(id=provisioning.device_id).first()

            device_provisioning_info = ProvisioningInfo(
                provisioning_id=str(provisioning.id),
                device=map_device_to_dict(device),
                qos_profile=provisioning.qos_profile,
                sink=provisioning.sink,
                sink_credential={
                    "credential_type": provisioning.sink_credential
                },
                started_at=provisioning.started_at,
                status=provisioning.status,
                status_info=provisioning_status_info
            )

            return device_provisioning_info
            
        else:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
            raise HTTPException(status_code=404, detail=f"Provisioning with ID {provisioning_id} not found.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching provisioning by ID: {e}")
        raise ValueError(f"Error fetching provisioning by ID: {e}")


def get_provisioning_by_device(db: Session, retrieve_provisioning_by_device: RetrieveProvisioningByDevice) -> ProvisioningInfo:
    """
    Fetch a provisioning by device ID.

    Args:
        db: Database session.
        retrieve_provisioning_by_device: The data needed to retrieve the provisioning.

    Returns:
        The ProvisioningInfo object or None if not found.
    """
    try:
        logger.debug(f"Received retrieve provisioning by device data: {retrieve_provisioning_by_device}\n")

        # Check if the device exists
        existing_device = db.query(Device).filter_by(phone_number=retrieve_provisioning_by_device.device.phone_number).first()

        if existing_device:
            provisioning = db.query(Provisioning).filter_by(device_id=existing_device.id).first()

            if provisioning:
                if provisioning.status_info:
                    provisioning_status_info = provisioning.status_info
                else:
                    provisioning_status_info = None
                    
                device_provisioning_info = ProvisioningInfo(
                    provisioning_id=str(provisioning.id),
                    device=map_device_to_dict(existing_device),
                    qos_profile=provisioning.qos_profile,
                    sink=provisioning.sink,
                    sink_credential={
                        "credential_type": provisioning.sink_credential
                    },
                    started_at=provisioning.started_at,
                    status=provisioning.status,
                    status_info=provisioning_status_info
                )

                return device_provisioning_info
        
        else:
            logger.debug(f"Device with phone number {retrieve_provisioning_by_device.device.phone_number} not found.\n")
            raise HTTPException(status_code=404, detail=f"Device with phone number {retrieve_provisioning_by_device.device.phone_number} not found.")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching provisioning by device: {e}")
        raise ValueError(f"Error fetching provisioning by device: {e}")


def delete_provisioning(db: Session, provisioning_id: str) -> None:
    """
    Deletes a provisioning (marks it as unavailable or removes it).

    Args:
        db: Database session.
        provisioning_id: The ID of the provisioning to delete.
    """
    try:
        logger.debug(f"Received to-be-deleted provisioning's id: {provisioning_id}\n")

        # Check if the provisioning exists
        provisioning = db.query(Provisioning).filter_by(id=provisioning_id).first()

        if not provisioning:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
            raise HTTPException(status_code=404, detail=f"Provisioning with ID {provisioning_id} not found.")

        # Check if the device already exists
        related_device = db.query(Device).filter_by(id=provisioning.device_id).first()

        if related_device:
            db.delete(provisioning)
            db.commit()
            logger.debug(f"Provisioning with ID {provisioning_id} has been deleted.\n")
            
            deleted_provisioning = ProvisioningInfo(
                provisioning_id=str(provisioning.id),
                    device=map_device_to_dict(related_device),
                    qos_profile=provisioning.qos_profile,
                    sink=provisioning.sink,
                    sink_credential={
                        "credential_type": provisioning.sink_credential
                    },
                started_at=provisioning.started_at,
                status=Status.REQUESTED,
                status_info=StatusInfo.DELETE_REQUESTED
            )

            return deleted_provisioning

        else:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting provisioning: {e}")
        raise ValueError(f"Error deleting provisioning: {e}")
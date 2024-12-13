# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 15:03:52
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-12-09 14:37:49

from sqlalchemy.orm import Session
from database.db import SessionLocal
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from datetime import datetime
from fastapi import HTTPException

from schemas.create_provisioning import CreateProvisioning
from database.base_models import Provisioning, Device
from schemas.provisioning_info import ProvisioningInfo
from schemas.status import Status
from schemas.status_changed import StatusChanged
from schemas.status_info import StatusInfo
from schemas.retrieve_provisioning_by_device import RetrieveProvisioningByDevice
from config import Config

# Set up logging
logger = Config.setup_logging()


def create_provisioning(db: Session, create_provisioning: CreateProvisioning) -> Provisioning:
    """
    Creates a new provisioning in the database.

    Args:
        db: Database session.
        create_provisioning: The data needed to create the provisioning.

    Returns:
        The created Provisioning object.
    """
    try:
        logger.debug(f"Received provisioning data: {create_provisioning}\n")

        # Check if the device already exists
        existing_device = db.query(Device)\
            .filter_by(phone_number=create_provisioning.device.phone_number)\
            .first()

        if existing_device:
            logger.debug(
                "Device with phone number %s already exists with ID %s",
                create_provisioning.device.phone_number,
                existing_device.id
            )
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

        # Create a new provisioning instance
        new_provisioning = Provisioning(
            qos_profile=create_provisioning.qos_profile,
            sink=create_provisioning.sink,
            device_id=new_device.id,
            sink_credential= \
                create_provisioning.sink_credential.credential_type
                if create_provisioning.sink_credential
                else None
        )

        # Add the new provisioning to the session
        db.add(new_provisioning)
        db.commit()
        db.refresh(new_provisioning)
        
        return new_provisioning

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating provisioning: {e}")
        raise ValueError(f"Error creating provisioning: {e}")

def get_all_provisionings(db: Session, provisioning_id: str) -> Provisioning:
    return db.query(Provisioning).all()

def update_provisioning_by_id(
    db: Session, provisioning_id: str, provisioning_status: str,
    provisioning_timestamp: str) -> tuple[Provisioning, Device]:
        provisioning, device = get_provisioning_by_id(db, provisioning_id)
        if provisioning:
            provisioning.started_at = datetime.fromisoformat(
                provisioning_timestamp.replace("Z", "+00:00")
            )
            provisioning.status = provisioning_status
            db.commit()
            db.refresh(provisioning)
        logger.info(
            f"Updated provisioning with id={provisioning_id} "
            f"to status={provisioning_status}"
        )
        return provisioning, device
            
            

def get_provisioning_by_id(db: Session, provisioning_id: str) -> tuple[Provisioning, Device]:
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
            device = db.query(Device).filter_by(id=provisioning.device_id).first()

            return provisioning, device
            
        else:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
            raise HTTPException(status_code=404, detail=f"Provisioning with ID {provisioning_id} not found.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching provisioning by ID: {e}")
        raise ValueError(f"Error fetching provisioning by ID: {e}")


def get_provisioning_by_device(db: Session, retrieve_provisioning_by_device: RetrieveProvisioningByDevice) -> tuple[Provisioning, Device]:
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
        if device_data.get("phoneNumber"):
            existing_device = db.query(Device).filter_by(
                phone_number=device_data["phoneNumber"]
            ).first()
        elif device_data.get("ipv4Address"):
            existing_device = db.query(Device).filter_by(
                ipv4_address=device_data["ipv4Address"]
            ).first()
        elif device_data.get("ipv6Address"):
            existing_device = db.query(Device).filter_by(
                ipv6_address=device_data["ipv6Address"]
            ).first()
        elif device_data.get("networkAccessIdentifier"):
            existing_device = db.query(Device).filter_by(
                network_access_identifier=device_data["networkAccessIdentifier"]
            ).first()

        if existing_device:
            provisioning = db.query(Provisioning).filter_by(device_id=existing_device.id).first()

            if provisioning:
                return provisioning, existing_device
        
        else:
            logger.debug(f"Device with phone number {retrieve_provisioning_by_device.device.phone_number} not found.\n")
            raise HTTPException(status_code=404, detail=f"Device with phone number {retrieve_provisioning_by_device.device.phone_number} not found.")
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching provisioning by device: {e}")
        raise ValueError(f"Error fetching provisioning by device: {e}")


def delete_provisioning(db: Session, provisioning_id: str) -> tuple[Provisioning, Device]:
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
            
            return provisioning, related_device

        else:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting provisioning: {e}")
        raise ValueError(f"Error deleting provisioning: {e}")
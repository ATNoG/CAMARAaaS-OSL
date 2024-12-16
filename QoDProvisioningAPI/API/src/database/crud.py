# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024

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


def retrieve_fields_to_check(device: Device) -> list:
    """
    Retrieves the list of fields to check for a given device.

    Args:
        device: The device object that contains the fields to be checked.

    Returns:
        A list of tuples, each containing the field name and its 
        corresponding value.
    """
    return [
        ("phone_number", device.phone_number),
        (
            "ipv4_public_address", 
            device.ipv4_address.public_address if device.ipv4_address else None
        ),
        (
            "ipv4_private_address", 
            device.ipv4_address.private_address if device.ipv4_address else None
        ),
        (
            "ipv4_public_port", 
            device.ipv4_address.public_port if device.ipv4_address else None
        ),
        ("ipv6_address", device.ipv6_address),
        ("network_access_identifier", device.network_access_identifier)
    ]
        

def find_existing_device(db: Session, fields_to_check: list) -> Device:
    """
    Find an existing device based on the fields provided.

    Args:
        db: Database session.
        fields_to_check: List of tuples with field names and values.

    Returns:
        The existing device if found, None otherwise.
    """
    for field, value in fields_to_check:
        if value:  # Only search if the field has a value
            existing_device = db.query(Device).filter_by(**{field: value})\
                .first()
            
            if existing_device:
                logger.debug(f"Existing device found: {existing_device}")

                return existing_device
    return None

def validate_device_fields(create_provisioning):
    """
    Validates the fields in the device object and assigns them to variables.

    Args:
        create_provisioning: The provisioning object containing the 
        device to validate.

    Returns:
        A dictionary containing the validated fields.
    """
    device = create_provisioning.device

    # Validate phone_number and network_access_identifier
    phone_number = device.phone_number if device.phone_number else None
    network_access_identifier = device.network_access_identifier \
        if device.network_access_identifier else None

    # Validate ipv4_address and its subfields
    ipv4_address = device.ipv4_address
    if ipv4_address:
        ipv4_public_address = ipv4_address.public_address \
            if ipv4_address.public_address else None
        ipv4_private_address = ipv4_address.private_address \
            if ipv4_address.private_address else None
        ipv4_public_port = ipv4_address.public_port \
            if ipv4_address.public_port else None
    else:
        ipv4_public_address = None
        ipv4_private_address = None
        ipv4_public_port = None

    # Validate ipv6_address
    ipv6_address = device.ipv6_address if device.ipv6_address else None

    # Return all the validated fields in a dictionary
    return {
        'phone_number': phone_number,
        'network_access_identifier': network_access_identifier,
        'ipv4_public_address': ipv4_public_address,
        'ipv4_private_address': ipv4_private_address,
        'ipv4_public_port': ipv4_public_port,
        'ipv6_address': ipv6_address
    }


def create_provisioning(
        db: Session, create_provisioning: CreateProvisioning
    ) -> Provisioning:
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

        device = create_provisioning.device

        fields_to_check = retrieve_fields_to_check(device)

        # Find an existing device if any field matches
        existing_device = find_existing_device(db, fields_to_check)

        # If device exists, check for field differences
        if existing_device:
            # Compare provided fields with the existing device fields
            differences = [
                (field, value, getattr(existing_device, field) != value)
                for field, value in fields_to_check
            ]
            
            # Check if there's at least one difference, 
            # and whether a new field is being added
            new_field_added = False
            for field, value, differs in differences:
                if differs:
                    existing_value = getattr(existing_device, field)
                    # Field doesn't exist in the existing device
                    if existing_value is None: 
                        logger.debug(
                            f"Adding new field {field} to existing device."
                        )
                        setattr(existing_device, field, value)
                        new_field_added = True
                    else:
                        # If any field differs, raise a conflict
                        logger.debug(
                            f"Device already exists, but fields differ: {field}"
                        )
                        raise HTTPException(
                            status_code=409,
                            detail="Device already exists, but fields differ."
                        )
            
            # If no differences found, reuse the existing device
            new_device = existing_device
        else:
            # Validate fields
            validated_fields = validate_device_fields(create_provisioning)

            # Create a new device instance using the validated fields
            new_device = Device(
                phone_number=validated_fields['phone_number'],
                network_access_identifier=validated_fields[
                    'network_access_identifier'
                ],
                ipv4_public_address=validated_fields['ipv4_public_address'],
                ipv4_private_address=validated_fields['ipv4_private_address'],
                ipv4_public_port=validated_fields['ipv4_public_port'],
                ipv6_address=validated_fields['ipv6_address']
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
    """
    Retrieves all provisioning records from the database.

    Args:
        db: Database session.
        provisioning_id: The ID of the provisioning to query. Although it's
        passed, it is not used in the query, and all provisionings are returned.

    Returns:
        A list of all provisioning records.
    """
    return db.query(Provisioning).all()

def update_provisioning_by_id(
    db: Session, provisioning_id: str, provisioning_status: str,
    provisioning_timestamp: str) -> tuple[Provisioning, Device]:
    """
    Updates the status and timestamp of a provisioning record by its ID.

    Args:
        db: Database session.
        provisioning_id: The ID of the provisioning to update.
        provisioning_status: The new status for the provisioning.
        provisioning_timestamp: The timestamp when the provisioning started.

    Returns:
        A tuple containing the updated Provisioning object and the associated
        Device object.

    Raises:
        HTTPException: If the fields of the existing device differ during an
        update.
    """
    provisioning, device = get_provisioning_by_id(db, provisioning_id)
    if provisioning:
        provisioning.started_at = datetime.fromisoformat(
            provisioning_timestamp.replace("Z", "+00:00")
        )
        provisioning.status = provisioning_status
        db.commit()
        db.refresh(provisioning)
    logger.debug(
        f"Updated provisioning with id={provisioning_id} "
        f"to status={provisioning_status}"
    )
    return provisioning, device
            
            

def get_provisioning_by_id(
        db: Session, provisioning_id: str
    ) -> tuple[Provisioning, Device]:
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
        provisioning = db.query(Provisioning).filter_by(id=provisioning_id)\
        .first()

        if provisioning:
            device = db.query(Device).filter_by(id=provisioning.device_id)\
            .first()

            return provisioning, device
            
        else:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
            raise HTTPException(
                status_code=404, 
                detail=f"Provisioning with ID {provisioning_id} not found."
            )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching provisioning by ID: {e}")
        raise ValueError(f"Error fetching provisioning by ID: {e}")


def get_provisioning_by_device(
        db: Session,
        retrieve_provisioning_by_device: RetrieveProvisioningByDevice
    ) -> tuple[Provisioning, Device]:
    """
    Fetch a provisioning by device ID.

    Args:
        db: Database session.
        retrieve_provisioning_by_device: The data needed to retrieve the
        provisioning.

    Returns:
        The ProvisioningInfo object or None if not found.
    """
    from fastapi import HTTPException

    # TODO: fix line length
    try:
        logger.debug(
            f"Received retrieve provisioning by device data: {retrieve_provisioning_by_device}\n"
        )

        # Validate if any field to search for is provided
        device = retrieve_provisioning_by_device.device
        if not (
            device.phone_number or 
            (device.ipv4_address and device.ipv4_address.public_address) or 
            (device.ipv4_address and device.ipv4_address.private_address) or 
            (device.ipv4_address and device.ipv4_address.public_port) or 
            device.ipv6_address or 
            device.network_access_identifier
        ):
            raise HTTPException(
                status_code=400, 
                detail="No search fields provided to retrieve the device."
            )

        fields_to_check = retrieve_fields_to_check(device)

        # Iterate through the fields to check for the provided values and query the DB
        for field, value in fields_to_check:
            if value:  # Only search if the field has a value
                existing_device = db.query(Device).filter_by(**{field: value})\
                    .first()
                # TODO: fix line length
                logger.debug(
                    f"Existing device found for field {field}: {existing_device}"
                )
                
                if existing_device:  # Stop searching as soon as we find a match
                    break

        # If a device was found, we need to check all fields to ensure they match
        if existing_device:
            # Compare all fields to check if any field differs
            differences = []
            for field, value in fields_to_check:
                if value and getattr(existing_device, field) != value:
                    differences.append((field, value))

            # If any field differs, raise a conflict (not found)
            if differences:
                logger.debug(f"Device fields differ: {differences}")
                raise HTTPException(
                    status_code=404,
                    detail="Device found, but fields differ."
                )
            
            logger.debug(
                "Device found and fields match, proceeding with provisioning."
            )
            provisioning = db.query(Provisioning)\
                .filter_by(device_id=existing_device.id).first()

            if provisioning:
                return provisioning, existing_device
        else:
            logger.debug("Device not found.\n")
            raise HTTPException(status_code=404, detail="Device not found.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error fetching provisioning by device: {e}")
        raise ValueError(f"Error fetching provisioning by device: {e}")



def delete_provisioning(
        db: Session, provisioning_id: str
    ) -> tuple[Provisioning, Device]:
    """
    Deletes a provisioning (marks it as unavailable or removes it).

    Args:
        db: Database session.
        provisioning_id: The ID of the provisioning to delete.
    """
    try:
        # TODO: fix line length
        logger.debug(f"Received to-be-deleted provisioning's id: {provisioning_id}\n")

        # Check if the provisioning exists
        provisioning = db.query(Provisioning).filter_by(id=provisioning_id)\
            .first()

        if not provisioning:
            logger.debug(f"Provisioning with ID {provisioning_id} not found.\n")
            raise HTTPException(
                status_code=404, 
                detail=f"Provisioning with ID {provisioning_id} not found."
            )

        # Check if the device already exists
        related_device = db.query(Device).filter_by(id=provisioning.device_id)\
            .first()

        if related_device:
            db.delete(provisioning)
            db.commit()
            # TODO: fix line length
            logger.debug(f"Provisioning with ID {provisioning_id} has been deleted.\n")
            
            return provisioning, related_device

        else:
            logger.debug(
                f"Provisioning with ID {provisioning_id} not found.\n"
            )
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting provisioning: {e}")
        raise ValueError(f"Error deleting provisioning: {e}")
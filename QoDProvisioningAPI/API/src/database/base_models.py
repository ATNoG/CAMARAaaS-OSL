# -*- coding: utf-8 -*-
# @Authors: 
#   Eduardo Santos (eduardosantoshf@av.it.pt)
#   Rafael Direito (rdireito@av.it.pt)
# @Organization:
#   Instituto de Telecomunicações, Aveiro (ITAv)
#   Aveiro, Portugal
# @Date:
#   December 2024

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from database.db import Base, engine
from schemas.status import Status
from schemas.status_info import StatusInfo
from enum import Enum as PyEnum
import uuid
from datetime import datetime
import re

class Device(Base):
    __tablename__ = 'device'
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, nullable=True)
    network_access_identifier = Column(String, nullable=True)
    ipv4_public_address = Column(String, nullable=True)
    ipv4_private_address = Column(String, nullable=True)
    ipv4_public_port = Column(Integer, nullable=True)
    ipv6_address = Column(String, nullable=True)

    provisioning = relationship('Provisioning', back_populates='device')


class Provisioning(Base):
    __tablename__ = 'provisioning'
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  
    qos_profile = Column(String(256), nullable=False)
    sink = Column(String, nullable=True)
    device_id = Column(Integer, ForeignKey('device.id'), nullable=True)
    sink_credential = Column(String, nullable=True, default=None)
    started_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SAEnum(Status), nullable=False, default=Status.REQUESTED)
    status_info = Column(SAEnum(StatusInfo), nullable=True)

    device = relationship('Device', back_populates='provisioning')


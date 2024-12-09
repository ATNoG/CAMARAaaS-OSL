# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 13:00:57
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-12-09 11:30:21

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
from openapi_server.database.db import Base
from openapi_server.database.schemas.status import Status
from openapi_server.database.schemas.status_info import StatusInfo
from enum import Enum as PyEnum
import uuid
from datetime import datetime
import re


class Device(Base):
    __tablename__ = 'device'

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

    id = Column(Integer, primary_key=True)
    qos_profile = Column(String(256), nullable=False)
    sink = Column(String, nullable=True)
    device_id = Column(Integer, ForeignKey('device.id'), nullable=True)
    sink_credential = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SAEnum(Status), nullable=False, default=Status.REQUESTED)
    status_info = Column(SAEnum(StatusInfo), nullable=True)

    device = relationship('Device', back_populates='provisioning')


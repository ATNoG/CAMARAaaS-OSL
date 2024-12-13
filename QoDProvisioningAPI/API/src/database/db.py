# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2024-11-28 12:00:36
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2024-11-28 16:41:47


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
import os
from config import Config

import logging

logger = Config.setup_logging()

sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel("WARNING")

for handler in logger.handlers:
    sqlalchemy_logger.addHandler(handler)

sqlalchemy_logger.propagate = True

# SQLite database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{Config.db_path}"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session and Base for models
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize the database
def init_db():
    import database.base_models
    Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

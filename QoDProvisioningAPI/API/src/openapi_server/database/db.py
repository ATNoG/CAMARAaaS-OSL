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

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)


# Path for SQLite database file (persisted volume)
DB_PATH = os.getenv("SQLITE_DB_PATH", "/data/sqlite.db")

# SQLite database URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session and Base for models
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Initialize the database
def init_db():
    import openapi_server.database.base_models
    
    Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

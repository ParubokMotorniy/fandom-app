"""DB connection logic"""
# db/connection.py

import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "page_retrieval_service_db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydb")
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")


DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
logger.info(f"Connecting to database at {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=5,  # Set a reasonable pool size
        max_overflow=10,  # Allow some additional connections
        connect_args={
            "server_settings": {
                "application_name": "page_retrieval_service",
                "client_encoding": "utf8"
            }
        }
    )
    logger.info("Database engine created successfully")
    logger.info(f"{DB_USER}, {DB_PASSWORD}, {DB_HOST}, {DB_PORT}, {DB_NAME}")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False  # Prevent expired object issues
)
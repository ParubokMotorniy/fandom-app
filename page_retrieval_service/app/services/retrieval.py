"""Core page-fetching logic"""

# app/services/retrieval.py

from app.db.connection import AsyncSessionLocal
from app.models.page import Page
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import uuid
import json
from confluent_kafka import Consumer, KafkaException
import threading
import os
from ..consul import consul_helpers as ch
import asyncio
from typing import Optional

# Global variable to store the Kafka consumer thread
kafka_thread: Optional[threading.Thread] = None

def get_kafka_consumer():
    """Get Kafka consumer configuration from Consul."""
    general_kafka_config = None
    while general_kafka_config is None:
        general_kafka_config = ch.read_value_for_key("kafka-config")
    
    consumer_config = {
        **general_kafka_config["kafka_parameters"],
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "group.id": "page-retrieval-service"
    }
    
    return Consumer(consumer_config)

async def process_kafka_message(message):
    """Process a message from Kafka and save it to the database."""
    try:
        page_data = json.loads(message.value().decode('utf-8'))
        return await save_page_to_db(page_data)
    except Exception as e:
        print(f"Error processing Kafka message: {e}")
        return False

def poll_messages():
    """Poll messages from Kafka topic."""
    print("Starting Kafka consumer...")
    consumer = get_kafka_consumer()
    
    # Get topic name from Consul config
    general_kafka_config = ch.read_value_for_key("kafka-config")
    topic_name = general_kafka_config["retrieve-topic-name"]
    
    print(f"Subscribing to topic: {topic_name}")
    consumer.subscribe([topic_name])
    
    while True:
        try:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                raise KafkaException(message.error())
            
            # Process message asynchronously
            print(f"Processing message: {message}")
            asyncio.run(process_kafka_message(message))
            
            consumer.commit(message)
        except Exception as e:
            print(f"Error polling Kafka messages: {e}")
            break
    
    consumer.close()

def start_kafka_consumer():
    """Start the Kafka consumer in a background thread."""
    global kafka_thread
    if kafka_thread is None or not kafka_thread.is_alive():
        kafka_thread = threading.Thread(target=poll_messages, daemon=True)
        kafka_thread.start()
        print("Kafka consumer thread started")

def stop_kafka_consumer():
    """Stop the Kafka consumer thread."""
    global kafka_thread
    if kafka_thread and kafka_thread.is_alive():
        # Note: This is a daemon thread, so it will be terminated when the main program exits
        print("Kafka consumer thread stopped")

async def get_page_by_id(page_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Page).where(Page.id == page_id)
        )
        return result.scalar_one_or_none()

async def save_page_to_db(page_data: dict) -> bool:
    """Save a new page to the database."""
    async with AsyncSessionLocal() as session:
        print(f"Saving page to db: {page_data}")
        try:
            new_page = Page(
                id=str(uuid.uuid4()),
                title=page_data["title"],
                content=page_data["html"]
            )
            print(f"Adding new page with id: {new_page.id}")
            session.add(new_page)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error saving page: {e}")
            await session.rollback()
            return False

async def fetch_all_pages():
    """Fetch all pages from the database."""
    async with AsyncSessionLocal() as session:
        print("Fetching all pages")
        try:
            result = await session.execute(select(Page))
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"Error fetching pages: {e}")
            return []
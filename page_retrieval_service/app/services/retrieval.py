"""Core page-fetching logic"""

# app/services/retrieval.py

from app.db.connection import AsyncSessionLocal, async_engine
from app.models.page import Page
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import uuid
import json
import threading
import logging
import os
from ..consul import consul_helpers as ch
import asyncio
from typing import Optional
from confluent_kafka import Consumer, KafkaException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Global variable to store the Kafka consumer thread
kafka_thread: Optional[threading.Thread] = None

def get_kafka_consumer():
    """Get Kafka consumer configuration from Consul."""
    kafka_config = None
    while kafka_config is None:
        kafka_config = ch.read_value_for_key("kafka-config")
    
    # Create consumer configuration
    consumer_config = {
        **kafka_config["kafka_parameters"],
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True
    }
    
    return Consumer(consumer_config)

async def process_message(message: str, session_factory):
    """Process a message from Kafka and save it to the database."""
    try:
        page_data = json.loads(message)
        async with session_factory() as session:
            return await save_page_to_db(page_data, session)
    except Exception as e:
        print(f"Error processing message: {e}")
        return False

def consume_messages():
    """Consume messages from Kafka topic."""
    print("Starting Kafka consumer...")
    consumer = get_kafka_consumer()
    
    # Get topic name from Consul config
    kafka_config = ch.read_value_for_key("kafka-config")
    topic_name = kafka_config["retrieve-topic-name"]
    
    # Subscribe to topic
    consumer.subscribe([topic_name])
    
    print(f"Consuming from topic: {topic_name}")
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Kafka error: {msg.error()}")
                raise KafkaException(msg.error())

            try:
                message = msg.value().decode("utf-8")
                print(f"Received message: {message}")

                # Schedule the coroutine to run on the main loop
                future = asyncio.run_coroutine_threadsafe(
                    process_message(message, AsyncSessionLocal),
                    kafka_loop
                )
                success = future.result()

                if success:
                    print("Message processed successfully")
                    consumer.commit(msg)
                else:
                    print("Failed to process message")
            except Exception as e:
                print(f"Error processing message: {e}")
    except Exception as e:
        print(f"Error consuming messages: {e}")
    finally:
        consumer.close()

def start_kafka_consumer():
    global kafka_thread, kafka_loop
    kafka_loop = asyncio.get_event_loop()
    if kafka_thread is None or not kafka_thread.is_alive():
        kafka_thread = threading.Thread(target=consume_messages, daemon=True)
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

async def save_page_to_db(page_data: dict, session=None) -> bool:
    """Save a new page to the database."""
    if session is None:
        async with AsyncSessionLocal() as session:
            return await _save_page_to_db_internal(page_data, session)
    return await _save_page_to_db_internal(page_data, session)

async def _save_page_to_db_internal(page_data: dict, session) -> bool:
    """Internal implementation of save_page_to_db."""
    print(f"Saving page to db: {page_data}")
    try:
        new_page = Page(
            title=page_data["title"],
            content=page_data["content"],
            id=page_data["id"]
        )
        print(f"Adding new page with id: {new_page.id}")
        session.add(new_page)
        try:
            await session.commit()
            print(f"Successfully committed page with id: {new_page.id}")
            return True
        except SQLAlchemyError as e:
            print(f"Error during commit: {str(e)}")
            print(f"Error type: {type(e)}")
            await session.rollback()
            return False
    except SQLAlchemyError as e:
        print(f"Error creating page: {str(e)}")
        print(f"Error type: {type(e)}")
        await session.rollback()
        return False
    except Exception as e:
        print(f"Unexpected error saving page: {str(e)}")
        print(f"Error type: {type(e)}")
        await session.rollback()
        return False

async def fetch_all_pages():
    """Fetch all pages from the database."""
    async with AsyncSessionLocal() as session:
        print("Fetching all pages")
        try:
            result = await session.execute(select(Page))
            pages = result.scalars().all()
            print(f"Found {len(pages)} pages")
            return pages
        except SQLAlchemyError as e:
            print(f"Error fetching pages: {e}")
            await session.rollback()
            return []
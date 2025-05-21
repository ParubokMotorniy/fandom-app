# app/services/add_page_logic.py

import json
from confluent_kafka import Producer
from app.schemas.page import PageCreate, PageResponse
from ..consul import consul_helpers as ch

def get_kafka_producer():
    """Get Kafka producer configuration from Consul."""
    kafka_config = None
    while kafka_config is None:
        kafka_config = ch.read_value_for_key("kafka-config")
    
    # Create producer configuration
    producer_config = {
        **kafka_config["kafka_parameters"]
    }
    
    return Producer(producer_config)

def forward_page_to_retrieval_service(page_data: PageCreate) -> bool:
    try:
        print("Getting Kafka producer")
        producer = get_kafka_producer()
        
        # Get the topic name from Consul config
        kafka_config = None
        while kafka_config is None:
            kafka_config = ch.read_value_for_key("kafka-config")
    
        topic_name = kafka_config["retrieve-topic-name"]
        print(f"Topic name: {topic_name}")
        
        # Convert page data to JSON
        page_json = json.dumps(page_data.dict())
        
        # Publish message to Kafka
        print(f"Publishing message to Kafka: {page_json}")
        producer.produce(
            topic=topic_name,
            value=page_json.encode('utf-8'),
            callback=lambda err, msg: print(f"Message delivery failed: {err}") if err else print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
        )
        
        # Wait for any outstanding messages to be delivered
        producer.flush()
        return True
        
    except Exception as e:
        print(f"Failed to send page to Kafka: {e}")
        return False

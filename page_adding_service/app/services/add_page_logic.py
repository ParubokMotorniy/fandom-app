# app/services/add_page_logic.py

import json
from confluent_kafka import Producer
from app.schemas.page import PageCreate, PageResponse
from ..consul import consul_helpers as ch

def get_kafka_producer():
    general_kafka_config = None
    while general_kafka_config is None:
        general_kafka_config = ch.read_value_for_key("kafka-config")
    
    producer_config = {
        **general_kafka_config["kafka_parameters"],
        "client.id": "page-adding-service"
    }
    
    return Producer(producer_config)

def forward_page_to_retrieval_service(page_data: PageCreate) -> bool:
    try:
        producer = get_kafka_producer()
        
        # Get the topic name from Consul config
        general_kafka_config = ch.read_value_for_key("kafka-config")
        topic_name = general_kafka_config["retrieve-topic-name"]
        
        # Convert page data to JSON
        page_json = json.dumps(page_data.dict())
        
        # Produce message to Kafka
        print(f"Producing message to Kafka: {page_json}")
        producer.produce(
            topic=topic_name,
            value=page_json.encode('utf-8'),
            callback=lambda err, msg: print(f"Message delivered to {msg.topic()} [{msg.partition()}]") if err is None else print(f"Failed to deliver message: {err}")
        )
        
        # Flush to ensure the message is sent
        producer.flush()
        return True
        
    except Exception as e:
        print(f"Failed to send page to Kafka: {e}")
        return False

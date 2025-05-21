import consul
import os
import json

def get_consul_client():
    return consul.Consul(
        host=os.environ.get("CONSUL_HOST", "localhost"),
        port=int(os.environ.get("CONSUL_PORT", 8500)),
    )

def read_value_for_key(key):
    client = get_consul_client()
    _, value = client.kv.get(key)
    if value is None:
        return {
            "search-topic-name" : "search-pages-topic",
            "retrieve-topic-name" : "retrieve-pages-topic",
            "kafka_parameters": 
            {
                "bootstrap.servers": "kafka:29092",
                "group.id": "kafka-servitor",
                "acks": "all"
            }
        }
    return json.loads(value['Value'].decode('utf-8')) 
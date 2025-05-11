from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer
import uuid
import json

app = FastAPI()

kafka_config = {
    "bootstrap.servers": "kafka:9096"
}

producer = Producer(kafka_config)

class PageData(BaseModel):
    url: str
    html: str

@app.post("/add_page")
async def add_page(data: PageData):
    try:
        page_id = str(uuid.uuid4())
        custom_uri = f"https://localhost/pages/{page_id}"

        payload = {
            "id": page_id,
            "original_url": data.url,
            "html": data.html,
            "custom_uri": custom_uri
        }

        producer.produce("user-post-topic", json.dumps(payload).encode("utf-8"))
        producer.flush(timeout=5)
        return {"status": "Page sent to Kafka successfully", "page_id": page_id, "custom_uri": custom_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")
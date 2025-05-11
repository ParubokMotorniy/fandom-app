from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from confluent_kafka import Producer
import uuid
import json
import base64

app = FastAPI()
kafka_config = {
    "bootstrap.servers": "kafka:9096"
}
producer = Producer(kafka_config)

class PageData(BaseModel):
    url: str
    html: str

@app.post("/add_page")
async def add_page(data: PageData, media: UploadFile = None):
    try:
        page_id = str(uuid.uuid4())
        # TODO get root url from consul
        custom_uri = f"https://localhost/pages/{page_id}"

        payload = {
            "id": page_id,
            "html": data.html,
            "custom_uri": custom_uri
        }
        # push without media to page-search
        producer.produce("page-search-topic", json.dumps(payload).encode("utf-8"))

        if media:
            media_content = await media.read()
            media_type = media.content_type
            media_filename = media.filename

            encoded_media = base64.b64encode(media_content).decode("utf-8")
            payload["media"] = {
                "filename": media_filename,
                "content_type": media_type,
                "data": encoded_media  # Now it's a string, ready for JSON
            }
        producer.produce("page-retrival-topic", json.dumps(payload).encode("utf-8"))

        producer.flush(timeout=5)

        return {"status": "Page sent to Kafka successfully", "page_id": page_id, "custom_uri": custom_uri}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {e}")

# app/main.py

from fastapi import FastAPI
from app.routes.pages import router as pages_router
from app.db.connection import async_engine
from app.models.page import Base
import uvicorn
import os
from app.consul import consul_helpers as ch
from app.services.retrieval import start_kafka_consumer, stop_kafka_consumer

app = FastAPI(
    title="Page Retrieval Service",
    description="Service to retrieve content pages and media",
    version="1.0.0",
)

app.include_router(pages_router, prefix="/api", tags=["Pages"])

@app.get("/health")
async def check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Page Retrieval Service starting up...")
    # Start Kafka consumer
    start_kafka_consumer()

    port = int(os.environ["INSTANCE_PORT"])
    print(f"port: {port}")
    #sevice-specific stuff
    ch.register_consul_service(
        f"page_retrieval" , 
        f"page_retrieval_{os.environ['INSTANCE_ID']}",
        os.environ["INSTANCE_HOST"], 
        port, 30, 60, "/health" 
    )

@app.on_event("shutdown")
async def shutdown_event():
    await async_engine.dispose()
    print("Page Retrieval Service shutting down...")
    # Stop Kafka consumer
    stop_kafka_consumer()

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

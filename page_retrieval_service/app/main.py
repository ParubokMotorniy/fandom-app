# app/main.py

from fastapi import FastAPI
from app.routes.pages import router as pages_router
from app.db.connection import async_engine
from app.models.page import Base
import uvicorn
from app.services.retrieval import start_kafka_consumer, stop_kafka_consumer

app = FastAPI(
    title="Page Retrieval Service",
    description="Service to retrieve content pages and media",
    version="1.0.0",
)

app.include_router(pages_router, prefix="/api", tags=["Pages"])

@app.on_event("startup")
async def startup_event():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Page Retrieval Service starting up...")
    # Start Kafka consumer
    start_kafka_consumer()

@app.on_event("shutdown")
async def shutdown_event():
    await async_engine.dispose()
    print("🛑 Page Retrieval Service shutting down...")
    # Stop Kafka consumer
    stop_kafka_consumer()

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

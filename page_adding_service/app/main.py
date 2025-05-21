# app/main

from fastapi import FastAPI
from app.routes import add_page
import os
from app.consul import consul_helpers as ch

app = FastAPI(
    title="Page Adding Service",
    description="Service to add content pages and media",
    version="1.0.0",
)

app.include_router(add_page.router, prefix="/api", tags=["Add Page"])

@app.on_event("startup")
async def startup_event():
    # e.g., test DB connection, preload data, etc.
    port = int(os.environ["INSTANCE_PORT"])
    print(f"port: {port}")
    ch.register_consul_service(
        "page_adding", 
        "page_adding_" + str(port - 8003),
        os.environ["INSTANCE_HOST"], 
        port
    )

    print("Page Adding Service starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    print("Page Adding Service shutting down...")

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
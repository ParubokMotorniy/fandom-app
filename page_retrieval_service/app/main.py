# app/main.py

from fastapi import FastAPI
from app.routes.pages import router as pages_router
from app.db.connection import engine
from app.models.page import Base
import uvicorn

app = FastAPI(
    title="Page Retrieval Service",
    description="Service to retrieve content pages and media",
    version="1.0.0",
)

app.include_router(pages_router, prefix="/api", tags=["Pages"])

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Page Retrieval Service starting up...")

@app.on_event("shutdown")
def shutdown_event():
    engine.dispose()
    print("🛑 Page Retrieval Service shutting down...")

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)

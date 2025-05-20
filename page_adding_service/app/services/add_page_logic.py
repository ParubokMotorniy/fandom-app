# app/services/add_page_logic.py

import httpx
import pydantic
from app.schemas.page import PageCreate, PageResponse

PAGE_SERVICE_URL = "http://page_retrieval_service:8001/api/internal/store-page"

async def forward_page_to_retrieval_service(page_data: PageCreate) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(PAGE_SERVICE_URL, json=page_data.dict())
            return response.status_code == 200
        except httpx.RequestError as e:
            print(f"Failed to reach page service: {e}")
            return False

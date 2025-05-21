# app/routes/add_page.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.add_page_logic import forward_page_to_retrieval_service, add_to_search_service
from app.schemas.page import PageCreate

router = APIRouter()

@router.post("/add-page")
async def add_page(request: PageCreate):
    print("Adding page")
    success = forward_page_to_retrieval_service(request)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add page")
    
    success = add_to_search_service(request)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add page to search service")
    
    print("Page added successfully")
    return {"message": "Page added successfully"}

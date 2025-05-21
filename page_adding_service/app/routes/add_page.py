# app/routes/add_page.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.add_page_logic import forward_page_to_retrieval_service, add_to_search_service
from app.schemas.page import PageCreate, PageResponse
import uuid

def generate_page_with_id(page_data: PageCreate):
    return PageResponse(title=page_data.title, content=page_data.html, id=str(uuid.uuid4()))

router = APIRouter()

@router.post("/add-page")
async def add_page(request: PageCreate):    
    new_page = generate_page_with_id(request) #to keep uuids consistent across the app -> both retrievers and search services share the same id
    
    print(f"Adding page: {new_page}")
    
    success = forward_page_to_retrieval_service(new_page)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add page")   
    
    success = add_to_search_service(new_page)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add page to search service") 
    
    print("Page added successfully to both topics")
    return {"message": "Page added successfully"}

@router.get("/health")
async def check():
    return "Page adding is healthy"

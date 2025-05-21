# app/routes/pages.py

from fastapi import APIRouter, HTTPException
from app.services.retrieval import get_page_by_id, save_page_to_db, fetch_all_pages
from app.schemas.page import PageCreate
from app.models.page import Page as DBPage
from app.schemas.page import PageResponse
from typing import List

router = APIRouter()

@router.get("/page/{page_id}")
async def fetch_page(page_id: str):
    page = await get_page_by_id(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.post("/internal/store-page", deprecated = True)
async def store_page(request: PageCreate):
    success = await save_page_to_db(request.dict())

    if not success:
        raise HTTPException(status_code=500, detail="Failed to save page")

    return {"status": "ok"}


@router.get("/pages", response_model=List[PageResponse], tags=["Pages"])
async def all_pages():
    pages = await fetch_all_pages()
    return [PageResponse(id=p.id, title=p.title, content=p.content) for p in pages]

@router.get("/health")
async def check():
    return "Page retrieval is healthy"

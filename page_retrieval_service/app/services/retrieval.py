"""Core page-fetching logic"""

# app/services/retrieval.py

from app.db.connection import AsyncSessionLocal
from app.models.page import Page
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
import uuid

async def get_page_by_id(page_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Page).where(Page.id == page_id)
        )
        return result.scalar_one_or_none()

async def save_page_to_db(page_data: dict) -> bool:
    """Save a new page to the database."""
    async with AsyncSessionLocal() as session:
        try:
            new_page = Page(
                id=str(uuid.uuid4()),
                title=page_data["title"],
                content=page_data["html"]
            )
            session.add(new_page)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error saving page: {e}")
            await session.rollback()
            return False

async def fetch_all_pages():
    """Fetch all pages from the database."""
    async with AsyncSessionLocal() as session:
        try:
            result = await session.execute(select(Page))
            return result.scalars().all()
        except SQLAlchemyError as e:
            print(f"Error fetching pages: {e}")
            return []
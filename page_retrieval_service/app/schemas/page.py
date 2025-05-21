from pydantic import BaseModel
from uuid import UUID

class PageCreate(BaseModel):
    title: str
    html: str

class PageResponse(BaseModel):
    id: UUID
    title: str
    content: str

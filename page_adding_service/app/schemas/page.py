from pydantic import BaseModel

class PageCreate(BaseModel):
    title: str
    html: str

class PageResponse(BaseModel):
    id: str
    title: str
    content: str

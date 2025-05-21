from pydantic import BaseModel

class PageResponse(BaseModel):
    id: str
    title: str
    content: str
    
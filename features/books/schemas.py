
from pydantic import BaseModel

class BookRequest(BaseModel):
    id: int | None = None
    title: str
    author: str
    description: str
    rating: int

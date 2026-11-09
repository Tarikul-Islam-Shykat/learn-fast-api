from fastapi import APIRouter

from features.books import services
from features.books.schemas import BookRequest


router = APIRouter(tags=["Books"])


@router.post("/books")
def create_book(book_request: BookRequest):
    return services.create_book(book_request.model_dump())


@router.get("/books/{book_id}")
async def get_book(book_id: int):
    return await services.read_book(book_id)


@router.get("/books")
async def get_books_by_rating(rating: int):
    return await services.read_book_by_rating(rating)


@router.put("/books/{book_id}")
def update_book(book_id: int, book_request: BookRequest):
    book_data = book_request.model_dump()
    return services.update_book(book_id, book_data)


@router.delete("/books/{book_id}")
def delete_book(book_id: int):
    services.delete_book(book_id)
    return None
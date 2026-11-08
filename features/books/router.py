
from fastapi import APIRouter
from features.books import services

router = APIRouter(tags=["Books"])

@router.post("/books")
def create_book(books : dict):
    return services.create_book(books)


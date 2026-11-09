_books = []


def create_book(book: dict):
    if book.get("id") is None:
        next_id = max(
            (item["id"] for item in _books if item.get("id") is not None),
            default=0,
        ) + 1
        book["id"] = next_id

    _books.append(book)
    return book


async def read_book(book_id: int):
    for book in _books:
        if book["id"] == book_id:
            return book

    return None


async def read_book_by_rating(rating: int):
    return [book for book in _books if book["rating"] == rating]


def update_book(book_id: int, book_data: dict):
    for index, book in enumerate(_books):
        if book["id"] == book_id:
            book_data["id"] = book_id
            _books[index] = book_data
            return book_data

    return None


def delete_book(book_id: int):
    for index, book in enumerate(_books):
        if book["id"] == book_id:
            _books.pop(index)
            return True

    return False
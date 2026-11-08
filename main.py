from fastapi import FastAPI
from core.errors import register_error_handlers
from features.users.router import router as users_router
from features.books.router import router as books_router

app = FastAPI()


register_error_handlers(app)

# register routers
app.include_router(users_router)
app.include_router(books_router)

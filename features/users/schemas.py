from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None


class UserUpdate(BaseModel):
    name: str
    email: str
    phone: str | None


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None = None
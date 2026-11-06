from fastapi import APIRouter, HTTPException

from features.users import services
from features.users.schemas import UserCreate, UserPublic, UserUpdate


router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[UserPublic])
def get_users(name: str | None = None):
    return services.list_users(name)


@router.get("/users/{user_id}", response_model=UserPublic)
def get_user(user_id: int):
    user = services.get_user(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/users", status_code=201, response_model=UserPublic)
def create_user(user_data: UserCreate):
    return services.create_user(user_data)


@router.put("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user_data: UserUpdate):
    user = services.update_user(user_id, user_data)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.delete("/users/{user_id}")
def delete_user(user_id: int):
    deleted = services.delete_user(user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {user_id} deleted"}

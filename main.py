from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel


class userCreate(BaseModel):
    name: str
    email: str
    phone : str | None = None



app = FastAPI()

users = [
    {"id": 1, "name": "Amina Rahman", "email": "amina@example.com"},
    {"id": 2, "name": "Rafi Ahmed asd", "email": "rafi@example.com"},
]




@app.get("/users")
# query parameter
def get_users(name: str | None = None ):
    if name is None:
        return users
    
    matching_users = []

    for user in users:
        if name.lower() in user["name"].lower():
            matching_users.append(user)
    
    return matching_users


@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user
    return {"error": "User not found"}


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user["id"] == user_id:
            users.pop(index)
            return {"message": f"User {user_id} deleted"}

    raise HTTPException(status_code=404, detail="User not found")




@app.post("/users", status_code=201)
def create_user(user: userCreate):
    new_user = {
        "id": len(users) + 1,
        "name": user.name,
        "email": user.email,
        "phone": user.phone
    }
    users.append(new_user)
    return new_user



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=422,
        content={
            "message": "Request validation failed",
            "errors": errors,
        },
    )


@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate):
    for user in users:
        if user["id"] == user_id:
            user["name"] = user_data.name
            user["email"] = user_data.email
            user["phone"] = user_data.phone
            return user

    raise HTTPException(status_code=404, detail="User not found")





def get_users():
    return users

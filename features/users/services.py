from features.users.schemas import UserCreate, UserUpdate


_users = [
    {
        "id": 1,
        "name": "Amina Rahman",
        "email": "amina@example.com",
        "phone": None,
    },
    {
        "id": 2,
        "name": "Rafi Ahmed asd",
        "email": "rafi@example.com",
        "phone": None,
    },
]


def list_users(name: str | None = None):
    if name is None:
        return _users

    matching_users = []

    for user in _users:
        if name.lower() in user["name"].lower():
            matching_users.append(user)

    return matching_users


def get_user(user_id: int):
    for user in _users:
        if user["id"] == user_id:
            return user

    return None


def create_user(user_data: UserCreate):
    next_id = max((user["id"] for user in _users), default=0) + 1

    new_user = {
        "id": next_id,
        "name": user_data.name,
        "email": user_data.email,
        "phone": user_data.phone,
    }

    _users.append(new_user)
    return new_user


def update_user(user_id: int, user_data: UserUpdate):
    for user in _users:
        if user["id"] == user_id:
            user["name"] = user_data.name
            user["email"] = user_data.email
            user["phone"] = user_data.phone
            return user

    return None


def delete_user(user_id: int):
    for index, user in enumerate(_users):
        if user["id"] == user_id:
            _users.pop(index)
            return True

    return False

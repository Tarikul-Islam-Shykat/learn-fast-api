# Section 4 — Authentication: Who Are You?

> **The journey:** register a user, store a password hash, exchange valid credentials for a signed token, then use that token to identify the user on later requests.

Section 3 made Todo data persistent. This section adds users and a way for the API to recognize who is making each request.

## The two questions behind security

| Term | Question | Example |
|---|---|---|
| Authentication | Who are you? | Verify a username and password; identify the user from a token |
| Authorization | What may you do? | Check whether the user owns a Todo or has the admin role |

Authentication comes first. Section 4 builds login and identity; Section 5 uses that identity to enforce ownership and roles.

## 1. Split routes into routers

As the app grows, group related routes in `APIRouter` objects and include them from `main.py`.

```text
main.py
  ├── auth router  -> registration and token endpoints
  └── todos router -> Todo endpoints
```

```python
app.include_router(auth.router)
app.include_router(todos.router)
```

Router prefixes and tags keep URLs and the API docs organized. For example, auth routes can use the `/auth` prefix and appear under an `auth` tag.

## 2. Users table and Todo ownership link

A user can own many Todos, while each Todo has one owner:

```text
USERS                                  TODOS
-----                                  -----
id (primary key)  1  ------------  many id (primary key)
username (unique)                       title
email (unique)                          owner_id (foreign key -> users.id)
hashed_password
is_active
role
```

The Todo table's `owner_id` is a **foreign key** pointing to `users.id`. A relationship in the SQLAlchemy models lets Python navigate between a user and their Todos. `username` and `email` should be unique if they identify accounts. Store a password hash, never a plaintext password.

Simplified SQLAlchemy model idea:

```python
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")

    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="todos")
```

The important database rule is `ForeignKey("users.id")`: it connects the Todo's owner ID to a real user row. The `relationship()` declarations describe the link for Python; the foreign key enforces the database connection.

## 3. Create users without storing plaintext passwords

The create-user request contains a plaintext password because the user is sending it during registration. Before saving, hash it and store only the hash.

```text
request password -> password hashing -> hashed_password column
```

Password hashes are one-way: during login, verify the submitted password against the stored hash. Do not decrypt a hash or compare a submitted password directly to the database value.

Conceptual helpers:

```python
def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(password, hashed_password)
```

The course uses bcrypt. Its imports and setup depend on the package versions used in the course. FastAPI's current security tutorial also demonstrates the same essential rule—hash on account creation and verify on login—using its current recommended password-hashing tools. [FastAPI security tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

When saving a user, map the request fields into the database model, hash the password, set `is_active`, and commit the session. Return safe user fields only; never return `hashed_password`. If the course gives its first account the `admin` role to demonstrate admin routes, treat that as demo setup. Public registration should assign an ordinary user role and never let the client choose `admin`.

## 4. Login: verify credentials and issue a token

The course's `/auth/token` endpoint uses `OAuth2PasswordRequestForm`. This form sends `username` and `password` as form data, rather than as a JSON request body.

```text
username + password
        |
        v
look up user -> verify password hash
        |
   invalid: 401
   valid: create access token
```

The token response is commonly shaped like:

```json
{
  "access_token": "<signed-token>",
  "token_type": "bearer"
}
```

`OAuth2PasswordBearer` describes how protected routes receive a bearer token from the `Authorization` header. It extracts the token; your code still has to decode it and identify the user.

If the token route is `/auth/token`, configure the OAuth2 helper's `tokenUrl` to point to that route so the API docs know where clients obtain a token.

## 5. JWT: the portable identity ticket

A JSON Web Token has three dot-separated parts:

```text
header.payload.signature
```

| Part | Purpose |
|---|---|
| Header | Says which signing algorithm is used, such as `HS256` |
| Payload | Holds claims such as `sub` (subject/user identifier) and `exp` (expiry time) |
| Signature | Lets the server detect whether the token was changed |

The payload is encoded, **not encrypted**. Do not put passwords, password hashes, or other secrets in it. A typical token carries a user identifier in `sub` and an expiry in `exp`. The JWT standard defines these claims and the token structure. [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519.html)

Token creation and verification, conceptually:

```python
payload = {"sub": user.username, "exp": expiration_time}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

Use a strong secret key kept outside source code for a deployed app. When decoding, allow only the expected algorithm and reject invalid signatures, expired tokens, or tokens without the required subject. The course uses `python-jose`; newer FastAPI examples use a different JWT package, so keep the encode/decode imports consistent with the course's dependencies.

## 6. Decode a token and get the current user

`get_current_user` is a reusable dependency:

1. `OAuth2PasswordBearer` extracts the bearer token.
2. Decode it and verify its signature and expiration.
3. Read the user identifier from `sub`.
4. Look up that user in the database.
5. Reject invalid credentials with `401 Unauthorized` and `WWW-Authenticate: Bearer`.

This dependency turns a token string into a trusted database user object that another route can use. A separate active-user dependency can reject accounts that are disabled.

```text
1. Client sends username + password form to /auth/token
2. API finds the user and verifies the password against its stored hash
3. If valid, API signs a JWT containing sub and exp
4. API returns access_token to the client
5. Client sends the token in Authorization: Bearer <token>
6. API verifies the signature and expiry, then loads the current user
```

## Section 4 checkpoint

Try to explain these without looking above:

1. How do authentication and authorization differ?
2. Why does the database store a password hash rather than the password?
3. What are the JWT header, payload, and signature for?
4. Why can a client read a JWT payload, and what should never be placed there?
5. What work does `get_current_user` do after extracting a token?
6. Why are routers included by `main.py` as the project grows?

## Official references

- [FastAPI OAuth2, password hashing, and bearer JWTs](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [FastAPI OAuth2 password form](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/)
- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519.html)
- [RFC 8725: JWT Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725.html)

## Related keywords

- **Router (`APIRouter`):** a group of related routes that `main.py` can include in the app.
- **Authentication:** establishing who is making the request.
- **Authorization:** deciding what that identified user is allowed to do.
- **Foreign key:** the Todo's `owner_id` value that points to `users.id`.
- **Relationship:** SQLAlchemy's Python-side way to navigate between related User and Todo objects.
- **Unique constraint:** database rule that prevents duplicate values such as usernames or emails.
- **Password hash:** one-way password representation stored in the database; a login verifies against it.
- **OAuth2 password form:** form-encoded `username` and `password` sent to the token endpoint in this course flow.
- **Bearer token:** access token sent in `Authorization: Bearer <token>`.
- **`OAuth2PasswordBearer`:** FastAPI helper that extracts the bearer token from a request; your code must still verify it.
- **JWT claim:** a value in the token payload, such as `sub` for the subject/user and `exp` for expiration.
- **JWT signature:** cryptographic check that detects token changes. A signed JWT payload is readable; it is not automatically encrypted.
- **401 Unauthorized:** credentials are missing or invalid.
- **Role:** user attribute, such as `user` or `admin`, used for authorization decisions.

## Questions you can ask while learning

- Why is password hashing different from encryption?
- What information is safe to put in a JWT payload if the client can read it?
- What does `OAuth2PasswordBearer` do, and what does it leave for `get_current_user` to do?
- Why should the server choose the user's role during registration?
- What should happen if the token is expired, has no `sub`, or refers to a user who no longer exists?

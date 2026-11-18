# Chapter: The Login System (OAuth2 and JWT)

> **The idea:** HTTP has no memory, so every request has to prove who sent it. The user logs in once, gets a **token**, and sends it with every later request.

The course app is a seller dashboard, so the examples use `Seller` as the user.

```text
1. Client posts email + password  → POST /login
2. Server checks them against the database
3. Server returns a token (encoded, contains user data)
4. Client sends the token in a header on every later request
5. Server reads the token → knows who it is → allows or blocks
```

Note: the code snippets below are standard patterns written for these notes. They have not been run end to end yet.

---

## 1. OAuth2 overview

OAuth2 is a standard for how login and tokens should work. This chapter uses the **password flow**: credentials in, token out, then the token in a header to reach protected routes.

Because FastAPI follows the standard, the `/docs` page can show an "Authorize" button that works with your login.

## 2. Password request form

The login route is a `POST` named `login`.

```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.email == form.username).first()
    ...
```

- It receives **form data**, not JSON, because the OAuth2 standard says so. You need `python-multipart` installed.
- The form always has fields named `username` and `password`. If your app logs in by email, the email arrives in `username`.
- You look the seller up with SQLAlchemy, then return a token.

## 3. Verify password

Two steps:
1. Find the seller by email. If there is none, raise an `HTTPException`.
2. Compare the typed password to the stored **hash**. If they don't match, raise an `HTTPException`.

```python
if not seller or not verify_password(form.password, seller.password_hash):
    raise HTTPException(status_code=401, detail="Invalid email or password")
```

- A hash is a one-way scramble, so the real password is never stored.
- `verify_password` hashes what the user typed and compares the two hashes (libraries like `bcrypt` or `pwdlib`).
- Use the **same message** for "no such email" and "wrong password". Different messages tell attackers which emails exist.
- If it passes, encode the seller's data into a token.

## 4. JWT

A JWT (JSON Web Token) is a string with three parts, made here with **PyJWT**:

```text
header . payload . signature
```

```python
import jwt
from datetime import datetime, timedelta, timezone

payload = {
    "sub": str(seller.id),
    "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

- **Header:** says which algorithm signed it.
- **Payload:** your data (the claims), such as the user id and `exp`, the expiry time.
- **Signature:** made from the header, payload and your **secret key**. If anyone edits the payload, the signature stops matching and the token is rejected.
- The payload is **encoded, not encrypted**. Anyone can read it. Never put a password or sensitive data in it.
- The secret key and the expiry time belong in **environment variables**, not in the code.

## 5. Password flow

How a protected endpoint checks the token. The client sends:

```http
Authorization: Bearer <token>
```

The server then:
1. Reads the header.
2. Decodes the token with the secret key.
3. Uses the data inside to identify the user.

No valid token means no access.

## 6. OAuth2 scheme

This piece pulls the token out of the header for you.

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/dashboard")
def dashboard(token: str = Depends(oauth2_scheme)):
    return {"token": token}
```

- `tokenUrl="login"` tells FastAPI and the `/docs` page which route issues tokens.
- Used as a dependency, it reads the `Authorization: Bearer ...` header and gives you the token string.
- If the header is missing, FastAPI answers `401` automatically.

## 7. Decode JWT

A `utils` module with two helpers: one makes tokens, one reads them.

```python
def generate_access_token(data: dict, expiry: timedelta = timedelta(minutes=30)) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + expiry}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
```

- `decode` checks the signature **and** the expiry.
- A tampered, wrong or expired token raises an error, and the helper turns that into `None`.
- Keeping this in one module means login and protected routes use the same code.

## 8. Identify user

Turn the decoded token into a real user from the database.

```python
data = decode_access_token(token)
seller = db.get(Seller, int(data["sub"]))     # fetch by primary key
```

- The token only holds an id, not the whole user.
- `session.get(Model, id)` is SQLAlchemy's quick lookup by primary key.
- Only trust the id after the signature has been verified.

## 9. User dependency

Put steps 6 to 8 in **one reusable function**.

```python
def get_current_seller(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Seller:
    data = decode_access_token(token)
    if data is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    seller = db.get(Seller, int(data["sub"]))
    if seller is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return seller


@app.get("/dashboard")
def dashboard(seller: Seller = Depends(get_current_seller)):
    return {"hello": seller.name}
```

A route that includes the dependency is protected. A route without it is public.

## 10. Token expiry

Tokens stop working after a set time.

- Put an `exp` claim in the payload, always in **UTC**, so servers in different time zones agree.
- On decode, PyJWT checks `exp` and raises `ExpiredSignatureError`. Treat it like an invalid token and return `401`.
- The client then has to log in again.
- A short expiry limits the damage if a token is stolen. 15 to 60 minutes is common.

## 11. API client authentication

How a client (Postman, a frontend) uses all of this:

1. Call `POST /login` with the form data and receive the token.
2. Save the token.
3. Send `Authorization: Bearer <token>` on every request.

```bash
curl -X POST http://127.0.0.1:8000/login -d "username=a@x.com&password=secret"
curl http://127.0.0.1:8000/dashboard -H "Authorization: Bearer <token>"
```

Many API clients can fetch the token and attach it automatically.

## 12. HTTP Bearer

This ties the chapter together:

- The scheme extracts the token from the header.
- Your dependency validates it.
- An invalid or missing token gets **`401 Unauthorized`**.

`HTTPBearer` is a simpler alternative to `OAuth2PasswordBearer`. It only asks for a token in `/docs`, without the username and password form. Use `OAuth2PasswordBearer` when FastAPI itself provides the login route.

---

## The whole picture

```text
login → verify password → make JWT (with exp) → client stores it
→ client sends Bearer token → scheme extracts → decode & verify
→ find user → route runs (or 401)
```

## Remember

- **Authentication** is who you are (login). **Authorization** is what you may do. This chapter is authentication.
- Hash passwords. Never store plain text.
- A JWT is **signed, not secret**.
- Keep the secret key out of code and out of git.
- Use HTTPS in production, or tokens can be stolen in transit.

## Common mistakes

- Sending JSON to the login route (it expects form data).
- Storing plain passwords instead of hashes.
- Putting the secret key in the code.
- Using a naive (non-UTC) datetime in `exp`.
- Returning different errors for "no such user" and "wrong password".
- Forgetting HTTPS in production.

## Quick self-check

1. Why does the login route use form data instead of JSON?
2. Why store a hash instead of the password?
3. Who can read a JWT's payload, and what does that mean for what you put in it?
4. What does the signature protect against?
5. What happens when a token's `exp` time has passed?
6. How does `Depends(get_current_seller)` make a route protected?

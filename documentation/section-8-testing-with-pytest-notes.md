# Section 8 — Testing with pytest

> **The rule:** a test is code that checks your code. Write it once, run it any time, and it tells you pass or fail.

## 1. Why test

Checking every endpoint by hand with curl does not scale. Tests re-check everything in seconds, and they catch bugs you introduce by accident, such as breaking login while editing todos.

## 2. Install and run

```bash
pip install pytest httpx
pytest        # run all tests
pytest -v     # more detail
```

`TestClient` needs `httpx`. Later lessons also use `pytest-asyncio`, for testing `async` functions.

## 3. Pytest basics

A test is a function whose name starts with `test_`. It uses a plain `assert`:

```python
def test_add():
    assert 1 + 1 == 2
```

Pytest finds files named `test_*.py` automatically. Tests can also be grouped in classes.

## 4. Testing a FastAPI app

`TestClient` calls your API in memory. No server needs to be running.

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
```

## 5. Key terms

- **assert:** the check inside a test.
- **fixture:** reusable setup code that tests receive as an argument.
- **TestClient:** a fake client that calls your app.
- **dependency override:** replace the real database or logged-in user with a test one.
- **pytest-asyncio:** lets pytest run `async` tests, such as `get_current_user`.

## 6. What the section covers

1. Pytest introduction and basics.
2. Testing a FastAPI app with `TestClient`.
3. Setup: making the project importable, fixtures, and dependency overrides (a separate test database and a fake user).
4. Testing the Todo project: each route, admin routes, and auth functions.
5. The last lessons test `get_current_user`: a valid JWT returns the right user, and a missing payload gives `401` with `could not validate user`.

## 7. How to practice with this project

The current project has `users` and `books` routes, so you can practice without a database:

- Test `GET /users` and check the status code and the list.
- Test `GET /users/999` for the 404.
- Test `POST /users` and check the 201 and the returned data.
- Test a validation error (a missing `name`) and check the 422 message from `core/errors.py`.
- Test books: create one, fetch it by id, and filter by rating.
- Write a test that expects `GET /books/999` to return 404. It fails today, because the route returns 200 with `null`. Fix the route and watch it pass.

Fixtures and dependency overrides need a database and auth. Practice those once that code exists. Fixtures also fix a problem you'll see: tests share the same in-memory list, so one test's data leaks into the next.

## Quick self-check

1. What must a test function's name start with?
2. What does `TestClient` do, and why is no server needed?
3. What is a dependency override for?
4. Why does testing `get_current_user` need `pytest-asyncio`?

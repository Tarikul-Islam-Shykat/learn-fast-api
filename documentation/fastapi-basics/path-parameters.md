# Path Parameters — Basic to Expert

> **The idea:** a path parameter is a variable part of the URL. It identifies **which one** thing you want: `/shipments/42` means "shipment number 42".

```text
GET /shipments/42
               └── path parameter: shipment_id = 42
```

## Path parameter vs query parameter

```text
GET /shipments/42?include_weight=false
               ──  ───────────────────
               │   query parameter (after the ?)
               path parameter (between the slashes)
```

| | Path parameter | Query parameter |
|---|---|---|
| Where | Inside the path, between `/` | After the `?` as `key=value`, joined by `&` |
| Purpose | **Which** item | **How** you want it (filter, sort, options) |
| Required? | Usually yes | Usually optional, with a default |
| Example | `/shipments/42` | `/shipments?status=shipped&limit=10` |

- Only the parts you declare with `{}` in the route are parameters. The other words are fixed.

  ```text
  Route:  /shipments/{shipment_id}/items/{item_id}
  URL:    /shipments/42/items/7
           ─────────  ──  ─────  ─
           fixed      param fixed param
  ```

- In FastAPI, a name inside `{}` in the route is a path parameter. A plain-typed argument that is **not** in the path is a query parameter.
- Real life, Amazon: `amazon.com/dp/B08N5WRWNW` picks one product (path). `amazon.com/s?k=laptop&sort=price` searches and sorts (query).

**In short:** the path says which item, and the query says how you want it.

---

All examples use one small fake database, like the course's shipment app:

```python
from fastapi import FastAPI

app = FastAPI()

shipments = {
    1: {"content": "laptop", "weight": 2.5, "status": "placed"},
    2: {"content": "books", "weight": 4.0, "status": "shipped"},
    3: {"content": "phone", "weight": 0.5, "status": "delivered"},
}
```

Run with `fastapi dev main.py`, then open `http://127.0.0.1:8000/docs` to try each route.

---

## Level 1 — Basic

### 1.1 A simple path parameter

**Real life:** a delivery tracking page, `/shipments/2`.

```python
@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int):
    return shipments[shipment_id]
```

- The name in `{shipment_id}` must match the function argument `shipment_id`.
- FastAPI takes `"2"` from the URL and gives the function the number `2`.

### 1.2 The type hint does the validation

The type hint decides what is accepted:

| Type hint | URL | Result |
|---|---|---|
| `int` | `/shipments/2` | ✅ `2` |
| `int` | `/shipments/abc` | ❌ 422 error |
| `int` | `/shipments/2.5` | ❌ 422 error |
| `float` | `/products/price/19.99` | ✅ `19.99` |
| `str` | `/users/shykat` | ✅ `"shykat"` (anything is accepted) |

Without a type hint, the value is always a string. You'd have to convert and check it yourself.

### 1.3 Common types, with real-life examples

```python
# str — a username on a social site: /users/shykat
@app.get("/users/{username}")
def get_user(username: str):
    return {"username": username}


# int — an order number: /orders/1001
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    return {"order_id": order_id}


# float — a weight in kg: /weight/2.5
@app.get("/weight/{kg}")
def convert_weight(kg: float):
    return {"kg": kg, "pounds": round(kg * 2.20462, 2)}
```

### 1.4 More than one path parameter

**Real life:** GitHub, `/{owner}/{repo}`.

```python
@app.get("/repos/{owner}/{repo}")
def get_repo(owner: str, repo: str):
    return {"owner": owner, "repo": repo}
```

`/repos/fastapi/fastapi` → `{"owner": "fastapi", "repo": "fastapi"}`

---

## Level 2 — Intermediate

### 2.1 Handle "not found" properly

Code 1.1 crashes with a 500 error when the id doesn't exist. Return a clear 404 instead:

```python
from fastapi import HTTPException


@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int):
    if shipment_id not in shipments:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipments[shipment_id]
```

- **422:** the value has the wrong *type* (`/shipments/abc`). FastAPI handles it.
- **404:** the type is right, but the *thing* doesn't exist (`/shipments/999`). You handle it.

### 2.2 Route ordering

FastAPI checks routes **top to bottom** and uses the first match.

```python
# ❌ Wrong order
@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int): ...

@app.get("/shipments/latest")      # never reached
def get_latest(): ...
```

`/shipments/latest` matches the first route, `"latest"` isn't an `int`, and you get a 422.

```python
# ✅ Fixed paths first, then dynamic ones
@app.get("/shipments/latest")
def get_latest():
    latest_id = max(shipments)
    return shipments[latest_id]


@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int): ...
```

### 2.3 Only allow fixed values with `Enum`

**Real life:** filter shipments by status. Only certain statuses exist.

```python
from enum import Enum


class ShipmentStatus(str, Enum):
    placed = "placed"
    shipped = "shipped"
    delivered = "delivered"


@app.get("/shipments/status/{status}")
def get_by_status(status: ShipmentStatus):
    return [s for s in shipments.values() if s["status"] == status.value]
```

- `/shipments/status/shipped` ✅
- `/shipments/status/lost` ❌ 422, with the allowed values listed
- `/docs` shows a dropdown of the allowed values.

### 2.4 Limit numbers with `Path`

**Real life:** an id can't be zero or negative, and a rating must be from 1 to 5.

```python
from typing import Annotated
from fastapi import Path


@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: Annotated[int, Path(gt=0)]):
    ...


@app.get("/ratings/{stars}")
def rate(stars: Annotated[int, Path(ge=1, le=5)]):
    return {"stars": stars}
```

| Option | Meaning |
|---|---|
| `gt` | greater than |
| `ge` | greater than or equal |
| `lt` | less than |
| `le` | less than or equal |

`/ratings/7` → 422, "Input should be less than or equal to 5".

### 2.5 Path and query parameters together

**Path** picks *which* item. **Query** (after `?`) adjusts *how* you get it.

```python
@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int, include_weight: bool = True):
    shipment = dict(shipments[shipment_id])
    if not include_weight:
        shipment.pop("weight")
    return shipment
```

`/shipments/1?include_weight=false`

Rule: if the name is in `{}` in the path, it's a path parameter. Otherwise it's a query parameter.

---

## Level 3 — Expert

### 3.1 Text patterns with `pattern`

**Real life:** tracking codes look like `TRK-12345`.

```python
@app.get("/track/{code}")
def track(code: Annotated[str, Path(pattern=r"^TRK-\d{5}$")]):
    return {"tracking_code": code}
```

- `/track/TRK-12345` ✅
- `/track/hello` ❌ 422

### 3.2 Special types: `UUID` and `date`

**Real life:** many real APIs use UUIDs instead of 1, 2, 3, so ids can't be guessed. Reports are often fetched by date.

```python
from uuid import UUID
from datetime import date


@app.get("/payments/{payment_id}")
def get_payment(payment_id: UUID):
    return {"payment_id": payment_id}


@app.get("/reports/{day}")
def daily_report(day: date):
    return {"day": day, "weekday": day.strftime("%A")}
```

- `/payments/3fa85f64-5717-4562-b3fc-2c963f66afa6` ✅, `/payments/123` ❌
- `/reports/2026-11-16` ✅ (you receive a real `date` object), `/reports/16-11-2026` ❌

### 3.3 Paths that contain `/`

**Real life:** a file storage app, `/files/photos/2026/trip.jpg`.

```python
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}
```

`:path` lets the parameter include slashes. Without it, `/files/photos/trip.jpg` would return 404.

### 3.4 Nested resources

**Real life:** an online shop. Orders belong to a customer, and items belong to an order.

```python
@app.get("/customers/{customer_id}/orders/{order_id}")
def get_customer_order(
    customer_id: Annotated[int, Path(gt=0)],
    order_id: Annotated[int, Path(gt=0)],
):
    return {"customer_id": customer_id, "order_id": order_id}
```

In real apps, also check that the order **belongs to** that customer. That's the ownership idea from the earlier course.

### 3.5 Reuse "find or 404" with a dependency

Many routes repeat the same "look up by id, or 404" code. Move it into one dependency:

```python
from fastapi import Depends


def get_shipment_or_404(shipment_id: Annotated[int, Path(gt=0)]) -> dict:
    if shipment_id not in shipments:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipments[shipment_id]


@app.get("/shipments/{shipment_id}")
def get_shipment(shipment: Annotated[dict, Depends(get_shipment_or_404)]):
    return shipment


@app.delete("/shipments/{shipment_id}")
def delete_shipment(
    shipment_id: int,
    shipment: Annotated[dict, Depends(get_shipment_or_404)],
):
    del shipments[shipment_id]
    return {"deleted": shipment}
```

The dependency reads `shipment_id` from the path itself. The check now lives in one place.

### 3.6 Path parameters in a router prefix

**Real life:** everything under one customer, `/customers/{customer_id}/...`.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/customers/{customer_id}")


@router.get("/orders")
def list_orders(customer_id: int):
    return {"customer_id": customer_id, "orders": []}


app.include_router(router)
```

`/customers/7/orders` → `customer_id = 7`

---

## Cheat sheet

| Need | Use |
|---|---|
| Any text | `name: str` |
| A whole number | `id: int` |
| A decimal | `price: float` |
| Only certain values | `Enum` |
| A number range | `Annotated[int, Path(ge=1, le=5)]` |
| A text format | `Annotated[str, Path(pattern=...)]` |
| An unguessable id | `UUID` |
| A date | `date` (format `YYYY-MM-DD`) |
| Slashes inside the value | `{file_path:path}` |
| A missing item | `HTTPException(status_code=404)` |
| The same check in many routes | `Depends(...)` |

## Practice — do these yourself

1. **Basic:** add `GET /products/{product_id}` with a dictionary of three products.
2. **Basic:** call it with `abc`, and note the 422 error message.
3. **Intermediate:** add a 404 for a missing product, and `GET /products/cheapest` (watch the route order).
4. **Intermediate:** add `GET /products/category/{category}` with an `Enum` of three categories.
5. **Expert:** add `GET /coupons/{code}` that only accepts codes like `SAVE10` or `SAVE25` (`^SAVE\d{2}$`).
6. **Expert:** move the "find product or 404" check into a dependency and use it in two routes.

After each one, open `/docs` and try good and bad values.

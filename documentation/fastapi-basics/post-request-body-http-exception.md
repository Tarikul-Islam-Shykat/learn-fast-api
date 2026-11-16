# HTTP Exception, POST, and Request Body

> **The idea:** until now your routes only read data (`GET`). This part teaches you to **send data to the API** and to **reply with proper errors**.

```text
PUT /shipments/42?notify=true        body: {"status": "shipped"}
               ──  ───────────             ────────────────────
               path   query                     request body
               which  options               the actual data
```

- **Path:** which item.
- **Query:** small options and filters.
- **Body:** the main data you create or update.

The examples use the same shipment app as the path parameters notes:

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

shipments = {
    1: {"content": "laptop", "weight": 2.5, "status": "placed"},
    2: {"content": "books", "weight": 4.0, "status": "shipped"},
}
```

Run with `fastapi dev main.py` and try every route in `http://127.0.0.1:8000/docs`.

---

## 1. HTTP methods: verbs

| Method | Meaning | Real life |
|---|---|---|
| `GET` | read | view shipment 42 |
| `POST` | create | create a new shipment |
| `PUT` | replace or update | change the shipment's status |
| `PATCH` | update part of it | change only the weight |
| `DELETE` | delete | cancel it |

`GET` has no body. `POST`, `PUT` and `PATCH` usually carry one.

---

## 2. HTTP Exception: proper errors

Without it, a missing id crashes with a 500. `HTTPException` sends a clean error instead:

```python
@app.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: int):
    if shipment_id not in shipments:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipments[shipment_id]
```

Response:

```json
{"detail": "Shipment not found"}
```

- `raise` stops the function right there. Nothing after it runs.
- Use the readable constants if you like: `status.HTTP_404_NOT_FOUND`.

| Code | Meaning | Use when |
|---|---|---|
| `200` | OK | the default for success |
| `201` | Created | a `POST` created something |
| `400` | Bad request | the request is wrong in a way you check yourself |
| `404` | Not found | the item doesn't exist |
| `422` | Validation error | FastAPI sends it when types or the body are wrong |

---

## 3. POST and the request body

`POST` creates something. The data goes in the **body** as JSON, not in the URL, so it can be large and structured.

```json
{"content": "laptop", "weight": 2.5}
```

You describe the body with a **Pydantic model**. FastAPI reads the JSON, validates it and gives your function a ready object.

```python
from pydantic import BaseModel


class ShipmentCreate(BaseModel):
    content: str
    weight: float


@app.post("/shipments", status_code=status.HTTP_201_CREATED)
def create_shipment(shipment: ShipmentCreate):
    new_id = max(shipments, default=0) + 1
    shipments[new_id] = {**shipment.model_dump(), "status": "placed"}
    return {"id": new_id, **shipments[new_id]}
```

Line by line:
- `shipment: ShipmentCreate` is a Pydantic model, so FastAPI reads it from the **body**.
- `status_code=201` is the right code for "created".
- `shipment.model_dump()` turns the model into a plain dictionary.
- The server makes the `id` and the starting `status`. The client doesn't send those.

Try it:

```bash
curl -X POST http://127.0.0.1:8000/shipments \
  -H "Content-Type: application/json" \
  -d '{"content": "camera", "weight": 1.2}'
```

```json
{"id": 3, "content": "camera", "weight": 1.2, "status": "placed"}
```

### What bad input looks like

| Body | Result |
|---|---|
| `{"content": "camera"}` | 422, `weight` field required |
| `{"content": "camera", "weight": "heavy"}` | 422, `weight` is not a number |
| Not valid JSON | 422, JSON decode error |

You wrote no checking code. The model's types are the validation.

---

## 4. Add rules to the model with `Field`

**Real life:** a courier only takes parcels up to 25 kg.

```python
from pydantic import BaseModel, Field


class ShipmentCreate(BaseModel):
    content: str = Field(min_length=2, max_length=30)
    weight: float = Field(gt=0, le=25)
```

| Option | Meaning |
|---|---|
| `min_length`, `max_length` | text length |
| `gt`, `ge`, `lt`, `le` | number limits |

`{"content": "x", "weight": -1}` → 422, with an error for each broken field.

---

## 5. Path, query and body together

**Real life:** update a shipment's status and optionally notify the customer.

```python
from enum import Enum


class ShipmentStatus(str, Enum):
    placed = "placed"
    shipped = "shipped"
    delivered = "delivered"


class StatusUpdate(BaseModel):
    status: ShipmentStatus


@app.put("/shipments/{shipment_id}")
def update_status(shipment_id: int, update: StatusUpdate, notify: bool = False):
    if shipment_id not in shipments:
        raise HTTPException(status_code=404, detail="Shipment not found")

    shipments[shipment_id]["status"] = update.status.value
    return {"id": shipment_id, **shipments[shipment_id], "notified": notify}
```

```bash
curl -X PUT "http://127.0.0.1:8000/shipments/1?notify=true" \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```

**How FastAPI decides where each value comes from:**

| Declared as | Read from |
|---|---|
| A name inside `{}` in the route (`shipment_id`) | the **path** |
| A plain type not in the path (`notify: bool`) | the **query** (after `?`) |
| A Pydantic model (`update: StatusUpdate`) | the **body** |

Both bad cases give an error: `{"status": "lost"}` → 422 (not an allowed status), and `/shipments/999` → 404.

---

## 6. Typical mistakes

- **Sending data in the URL for a `POST`.** The body is where the data goes.
- **Forgetting the `Content-Type: application/json` header** in curl.
- **Letting the client choose the `id`.** The server should assign it.
- **Using 200 for a create.** Use 201.
- **Mixing up 404 and 422.** 404 means the thing doesn't exist. 422 means the request is malformed.

## Cheat sheet

| Need | Use |
|---|---|
| Return an error | `raise HTTPException(status_code=..., detail="...")` |
| Create something | `@app.post(..., status_code=201)` |
| Describe the body | a class that extends `BaseModel` |
| Rules on body fields | `Field(min_length=..., gt=...)` |
| Fixed allowed values | `Enum` |
| Pydantic model to dictionary | `model.model_dump()` |

## Practice — do these yourself

1. Add `POST /products` with a model of `name: str` and `price: float`. Return 201 and a new id.
2. Send a body with `price` missing, then `price: "free"`. Read both 422 messages.
3. Add `Field(gt=0)` to `price` and a `min_length=2` rule to `name`.
4. Add `PUT /products/{product_id}` that updates the price, with a 404 for a missing product.
5. Add a query parameter `?discount=true` to that route that cuts the price by 10%.
6. Look at the `/docs` page and find where path, query and body are shown for your `PUT` route.

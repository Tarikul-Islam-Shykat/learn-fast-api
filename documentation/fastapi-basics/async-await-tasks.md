# Async Programming: async, await, Tasks, Task Groups

> **The idea:** most of what an API does is **waiting** (database, network, files). Async lets Python switch to other work while one task waits, instead of sitting idle.

FastAPI **supports** async. It doesn't require it. You can write normal `def` routes or `async def` routes.

## 1. The restaurant picture

- **Synchronous:** the waiter takes your order, stands at the kitchen until the food is ready, then goes to the next table.
- **Asynchronous:** the waiter takes your order, goes to the next table while the kitchen cooks, and returns when the food is ready.

It's still one waiter. They stop wasting time waiting.

**Concurrency is not parallelism.** Async doesn't do two things at the same instant. It switches to another task whenever the current one is waiting. It helps with **waiting**, not with heavy calculations.

---

## 2. Synchronous code: one line at a time

```python
import time

def fetch_sync(name):
    time.sleep(1)          # pretend this is a slow database
    return name

results = [fetch_sync(n) for n in "ABC"]   # 3 seconds
```

Each call blocks until it finishes. Three one-second waits take **3 seconds**.

---

## 3. `async` and `await`

```python
import asyncio

async def fetch(name):
    await asyncio.sleep(1)   # waiting, but others can run meanwhile
    return name

print(asyncio.run(fetch("A")))
```

- `async def` makes a **coroutine**: a function that can pause.
- `await` means "pause here until this finishes, and let other tasks run meanwhile".
- `asyncio.run(...)` starts the event loop and runs the coroutine. Use it at the top of a script.

### Common mistake: forgetting `await`

```python
async def forgot():
    return fetch("A")        # no await
```

This returns `<coroutine object fetch ...>` and the code **never runs**. Python also warns "coroutine ... was never awaited".

### Awaiting one after another is still slow

```python
async def sequential():
    return [await fetch(n) for n in "ABC"]   # 3 seconds
```

`await` pauses **this** function until the call is done. Three awaits in a row still take 3 seconds. To overlap the waits, you need tasks.

---

## 4. Tasks: run several at the same time

```python
async def with_tasks():
    tasks = [asyncio.create_task(fetch(n)) for n in "ABC"]
    return [await t for t in tasks]          # about 1 second
```

`create_task` **starts** the coroutine running right away. All three wait together.

```text
Sequential:  A ─1s─ B ─1s─ C ─1s─  = 3 seconds
Tasks:       A ─1s─
             B ─1s─                 = 1 second
             C ─1s─
```

A shorter way to do the same is `asyncio.gather`:

```python
async def with_gather():
    return await asyncio.gather(fetch("A"), fetch("B"), fetch("C"))   # about 1 second
```

---

## 5. Task group: the safer way

```python
async def with_group():
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(n)) for n in "ABC"]
    return [t.result() for t in tasks]       # about 1 second
```

- `async with` waits for **all** tasks to finish when the block ends.
- If one task fails, the others are **cancelled**. Plain `create_task` doesn't do this.
- It needs Python 3.11 or newer.

I ran all of these. The sync version took 3.0s, the sequential awaits took 3.0s, and the tasks, `gather` and task group each took 1.0s.

---

## 6. Async in FastAPI

```python
import asyncio, time
from fastapi import FastAPI

app = FastAPI()


@app.get("/async-good")
async def async_good():
    await asyncio.sleep(1)       # waits without blocking the server
    return {"ok": True}


@app.get("/sync-def")
def sync_def():
    time.sleep(1)                # FastAPI runs this in a thread, so the server stays free
    return {"ok": True}


@app.get("/blocking-bad")
async def blocking_bad():
    time.sleep(1)                # ❌ blocks the whole server
    return {"ok": True}
```

I sent 3 requests to each route at the same time:

| Route | Time for 3 requests |
|---|---|
| `/async-good` | 1.0s |
| `/sync-def` | 1.0s |
| `/blocking-bad` | **3.0s** |

**The main lesson:** a blocking call like `time.sleep()` inside `async def` freezes every request until it ends. Inside `async def`, use `await asyncio.sleep()` or an async library.

### Running several waits inside one route

**Real life:** a dashboard needs a shipment, its customer and its location, from three slow sources.

```python
async def get_shipment(): await asyncio.sleep(1); return {"id": 1}
async def get_customer(): await asyncio.sleep(1); return {"name": "Amina"}
async def get_location(): await asyncio.sleep(1); return {"city": "Dhaka"}


@app.get("/dashboard")
async def dashboard():
    async with asyncio.TaskGroup() as tg:
        shipment = tg.create_task(get_shipment())
        customer = tg.create_task(get_customer())
        location = tg.create_task(get_location())

    return {
        "shipment": shipment.result(),
        "customer": customer.result(),
        "location": location.result(),
    }
```

This responds in about 1 second instead of 3.

---

## When to use which

| Situation | Use |
|---|---|
| Normal blocking code (a regular database library) | `def` route |
| An async library (async database, `httpx.AsyncClient`) | `async def` route with `await` |
| Several independent waits in one route | `TaskGroup` (or `gather`) |
| Heavy calculation | neither helps, it needs separate processes |

## Cheat sheet

| Need | Use |
|---|---|
| Make a function that can pause | `async def` |
| Wait for a coroutine | `await` |
| Run a coroutine from a script | `asyncio.run(...)` |
| Start work in the background | `asyncio.create_task(...)` |
| Wait for several at once | `asyncio.gather(...)` or `TaskGroup` |
| Safe waiting inside async code | `await asyncio.sleep(...)` |

## Practice — do these yourself

1. Run section 2, then section 3. Time both with `time.perf_counter()`.
2. Remove `await` from a call and read the warning.
3. Change `sequential` to use tasks and watch 3 seconds become 1.
4. Add a route to your app with `time.sleep(2)` inside `async def`. Call it from two terminals at once, then change it to `await asyncio.sleep(2)` and compare.
5. Build the `/dashboard` route and time it.

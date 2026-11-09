# Users API curl examples

Start the app from the project root:

```bash
uvicorn main:app --reload
```

The examples use `http://127.0.0.1:8000`. User data is in memory, so create, update, and delete changes reset when the app restarts.

## List users

```bash
curl -i http://127.0.0.1:8000/users
```

## Filter users by name

```bash
curl -i "http://127.0.0.1:8000/users?name=amina"
```

## Get one user

```bash
curl -i http://127.0.0.1:8000/users/1
```

## Create a user

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Sara Khan","email":"sara@example.com","phone":null}'
```

Expected status: `201 Created`. The response includes the new user and its assigned ID.

## Update a user

`PUT` expects the full user body. Include `phone`, even when its value is `null`.

```bash
curl -i -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Amina Rahman","email":"amina@example.com","phone":null}'
```

Expected status: `200 OK`.

## Delete a user

```bash
curl -i -X DELETE http://127.0.0.1:8000/users/1
```

Expected status: `200 OK`, with a message confirming deletion.

## Try a missing user

```bash
curl -i http://127.0.0.1:8000/users/999
```

Expected status: `404 Not Found`.

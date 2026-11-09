# Books API curl examples

Start the app from the project root:

```bash
uvicorn main:app --reload
```

The examples use `http://127.0.0.1:8000`. Books are stored in memory and reset when the app restarts. Start with a fresh app process and run the POST example first; the remaining examples use the first assigned ID, `1`.

## Create a book

The service assigns an ID when you omit it.

```bash
curl -i -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title":"The Hobbit","author":"J. R. R. Tolkien","description":"A fantasy novel","rating":5}'
```

Expected status: `200 OK`; the response returns the book object.

## Get a book by ID

```bash
curl -i http://127.0.0.1:8000/books/1
```

## Get books by rating

```bash
curl -i "http://127.0.0.1:8000/books?rating=5"
```

## Update a book

`PUT` expects the full book body. The ID in the URL identifies which book to update.

```bash
curl -i -X PUT http://127.0.0.1:8000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"id":1,"title":"The Hobbit","author":"J. R. R. Tolkien","description":"Updated description","rating":4}'
```

## Delete a book

```bash
curl -i -X DELETE http://127.0.0.1:8000/books/1
```

The route is written to return `200 OK` with a `null` response body.

Unknown book IDs currently return `null` with a `200 OK` response. HTTP exception handling for missing books comes later in the course.

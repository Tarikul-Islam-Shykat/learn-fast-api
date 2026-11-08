# FastAPI learning notes

## Schema and Pydantic

- A **schema** describes the shape of data: its fields and their types.
- **Pydantic** models define those schemas and validate data sent to or returned from the API.
- In this project, `UserCreate` describes user input, while `UserPublic` describes user data returned by the API.
- A schema is not a database table and does not store data.

## Database and ORM

- A **database** stores data so it remains available after the app restarts. This project currently stores users in a Python list, so changes are temporary.
- An **ORM** maps database records to Python objects and helps perform database operations.
- **SQLAlchemy** is commonly used with SQL databases such as SQLite or PostgreSQL. FastAPI does not require it.

### Do I need an ORM?

An ORM is optional. It helps your app work with database records through Python objects instead of writing SQL for every operation. SQLAlchemy is for SQL databases; for MongoDB, use the PyMongo driver instead. You do not need either one while this project stores users in a Python list.

### What are a Pydantic model and a schema?

A **schema** is the description of the data shape: its fields and types. A **Pydantic model** is a Python class that defines that schema and lets FastAPI validate data. In this project, `UserCreate` is a Pydantic model defining the schema for user input. It validates data; it does not store it in a database.

## MongoDB

- MongoDB stores flexible documents in collections rather than rows in fixed tables.
- To use MongoDB from Python, connect with **PyMongo**. SQLAlchemy is not required.
- A Pydantic schema can validate a user, then PyMongo can insert it as a document:

  ```python
  user = UserCreate(name="Amina", email="amina@example.com")
  users_collection.insert_one(user.model_dump())
  ```

- The app also needs code to find, update, and delete documents. PyMongo provides these operations.

## Request flow

```text
request -> Pydantic validation -> route -> service -> database
```

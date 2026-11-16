# Section 6 — Production DBMS: PostgreSQL and MySQL

> **The rule:** only the connection URL and the driver change when you switch databases. Models, routes, and CRUD code stay the same.

Sections 2–5 used SQLite. Section 6 moves the same Todo app to PostgreSQL and MySQL. This section is setup work, not new FastAPI concepts.

## 1. SQLite versus a database server

| | SQLite | PostgreSQL / MySQL |
|---|---|---|
| Architecture | A single file, no server | A separate server your app connects to |
| Concurrency | Weak with many writers | Built for many concurrent users |
| Security | File permissions only | Users, passwords, roles |
| Use | Learning, prototypes | Production |

## 2. What changes in `database.py`

```python
"sqlite:///./todosapp.db"                                            # SQLite
"postgresql://USER:PASSWORD@localhost/TodoApplicationDatabase"       # PostgreSQL
"mysql+pymysql://USER:PASSWORD@127.0.0.1:3306/TodoApplicationDatabase"  # MySQL
```

```text
dialect+driver://username:password@host:port/database_name
```

| | PostgreSQL | MySQL |
|---|---|---|
| Driver | `psycopg2-binary` | `PyMySQL` |
| Default port | 5432 | 3306 |
| GUI tool | pgAdmin | MySQL Workbench |
| Auto ID | `SERIAL` | `AUTO_INCREMENT` |

Remove SQLite's `connect_args={"check_same_thread": False}` when switching.

## 3. Steps for each database

1. Install the server (Windows installer, or Postgres.app on Mac for PostgreSQL). Set the password.
2. Create a database for the app.
3. Create the `users` and `todos` tables. `todos.owner_id` is a **foreign key** to `users.id`, so every todo belongs to a real user.
4. Install the driver in your `.venv`.
5. Change the URL in `database.py` and run `uvicorn main:app --reload`.
6. Create a user and todos through the API, then check the rows in pgAdmin or Workbench.

## Common problems

- **Connection refused:** the server isn't running, or the port is wrong.
- **Authentication failed:** wrong username or password in the URL.
- **`ModuleNotFoundError`:** the driver isn't installed in the active `.venv`.

## Quick self-check

1. What two things change in `database.py` when you switch databases?
2. What does the `owner_id` foreign key guarantee?
3. What is the difference between SQLite and PostgreSQL or MySQL?

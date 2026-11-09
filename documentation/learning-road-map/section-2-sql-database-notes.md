# Section 2: SQL databases and SQLAlchemy

These notes cover the ideas behind the database lessons. The Todo app will use SQLite for storage and SQLAlchemy to work with it from Python.

## 1. Database, DBMS, tables, and SQL

- A **database** stores organized data.
- A **DBMS** is software that manages a database. SQLite, MySQL, and PostgreSQL are database systems.
- A **relational database** stores data in tables. Columns describe fields; rows hold individual records.
- A **primary key** such as `id` uniquely identifies a row.
- **SQL** is the language used to create, read, update, and delete relational data.

```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER NOT NULL DEFAULT 1,
    complete INTEGER NOT NULL DEFAULT 0
);

INSERT INTO todos (title, description, priority, complete)
VALUES ('Learn SQL', 'Practice the basics', 2, 0);

SELECT * FROM todos;
SELECT * FROM todos WHERE id = 1;

UPDATE todos SET complete = 1 WHERE id = 1;
DELETE FROM todos WHERE id = 1;
```

Be careful with `UPDATE` and `DELETE`: without a `WHERE` condition, the command may affect every row.

## 2. SQLite

SQLite is a database engine that stores a database in a file and does not need a separate database server. This makes it useful for learning and small applications.

The macOS terminal lesson lets you work with the same database file directly:

```text
sqlite3 todos.db
.tables
.schema todos
.mode table
SELECT * FROM todos;
.quit
```

Use the course's macOS installation lesson if the `sqlite3` command is not available. The MySQL and PostgreSQL names in the introduction are other relational DBMSs; this section starts with SQLite.

## 3. What SQLAlchemy does

SQLAlchemy maps Python classes to SQL tables and Python objects to table rows. It can issue SQL for common operations, while SQL and relational database concepts still apply.

The course creates these parts in `database.py`:

- **Engine:** knows how to connect to a database. The SQLite URL points to a file such as `todos.db`.
- **`connect_args`:** extra settings for the connection. The course uses `{"check_same_thread": False}` for SQLite with FastAPI.
- **`SessionLocal`:** a factory for database sessions. A session is used to read data, track changes, and commit a transaction.
- **`Base`:** the common base class for SQLAlchemy table models; it tracks their table definitions.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()
```

## 4. The Todo table model

A SQLAlchemy model describes how a table is stored. `__tablename__` names the table, and each `Column` describes one column.

```python
from sqlalchemy import Boolean, Column, Integer, String

from database import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    priority = Column(Integer, default=1)
    complete = Column(Boolean, default=False)
```

## 5. Creating the table and using a session

`Base.metadata.create_all(bind=engine)` creates tables for models registered with `Base` when they do not already exist. Import the model before calling `create_all` so SQLAlchemy knows its table definition. `create_all` creates missing tables; it is not a tool for changing existing tables when your model changes.

A session is typically opened for an operation or request, then closed. Changes are persisted by committing the session. If an operation fails, a session can be rolled back before it is closed.

## 6. How a FastAPI request reaches the database

```text
HTTP request
  -> Pydantic validates the request data
  -> route gets a SQLAlchemy session
  -> SQLAlchemy reads or changes Todo rows
  -> session commits changes
  -> FastAPI returns a response
```

**Pydantic models** describe and validate API data. **SQLAlchemy models** describe data stored in database tables. They can have similar fields, but they have different jobs.

The key change from your Books feature is persistence: books held in a Python list disappear on app restart; rows in the SQLite file remain.

## Learning checkpoint

Try to explain these in your own words:

1. What is the difference between SQL and SQLAlchemy?
2. What do the engine, session, and `Base` each do?
3. How does a SQL `SELECT` relate to reading a Todo through SQLAlchemy?
4. Why does a SQLite Todo remain after restarting the app while a list item does not?

## Official references

- [SQLite overview](https://www.sqlite.org/about.html)
- [FastAPI SQL databases guide](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy ORM overview](https://docs.sqlalchemy.org/en/20/orm/)
- [SQLAlchemy session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

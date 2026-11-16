# Section 7 — Alembic Data Migration

> **The rule:** Git tracks changes to your code. Alembic tracks changes to your database structure.

## 1. The problem

Tables are created from SQLAlchemy models. If you later add a column to a model, `create_all()` will not change a table that already exists. The code and the database no longer match.

Fixing it by deleting the database loses all the data. Running `ALTER TABLE` by hand is easy to forget and leaves no history.

## 2. What Alembic is

A migration tool for SQLAlchemy. Each change to the database structure is written as a small, versioned script called a **revision**. Alembic applies the revisions in order.

Why it helps:

- **Data survives.** You change the structure without deleting rows.
- **Same change everywhere.** Every machine runs the same migration files.
- **History.** The files live in git.
- **Undo.** A change can be rolled back.

## 3. Install and set up

```bash
pip install alembic
alembic init alembic
```

This creates an `alembic/` folder and an `alembic.ini` file. Two things must be configured:

- The database URL, in `alembic.ini` (`sqlalchemy.url`).
- `target_metadata = Base.metadata` in `alembic/env.py`, so Alembic knows about your models.

## 4. Revisions

A revision is one migration file with two functions:

```python
def upgrade():
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable=True))


def downgrade():
    op.drop_column("users", "phone_number")
```

- `upgrade()` applies the change.
- `downgrade()` undoes it.
- Revisions are chained. Each one records which revision came before it.

Create one:

```bash
alembic revision -m "add phone number to users"
```

## 5. Upgrade and downgrade

```bash
alembic upgrade head      # apply all new revisions
alembic downgrade -1      # undo the last revision
alembic current           # show the current revision
alembic history           # list all revisions
```

## Common problems

- **Wrong database URL** in `alembic.ini`.
- **`target_metadata` not set** to your models' `Base.metadata`.
- **Empty `downgrade()`:** the change can't be undone.

## Quick self-check

1. Why doesn't `create_all()` solve schema changes?
2. What do `upgrade()` and `downgrade()` do?
3. What does `alembic upgrade head` do?
4. Why keep migration files in git?

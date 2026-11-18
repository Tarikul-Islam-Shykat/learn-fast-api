# How to Start a Backend Project

> **The rule:** don't start with tables or code. Start with **what the app does**. Then find the things it stores, and connect them.

The data shape is the hardest part to change later. A route is easy to change. A table that already holds real users' data needs a migration. So a little thinking first saves a lot of pain.

## The steps

```text
1. What does the app do?       (features, in plain words)
2. What are the entities?      (the nouns)
3. What are their fields?
4. How do they relate?         (one-to-many, many-to-many, one-to-one)
5. Draw it                     (ERD)
6. Turn it into tables         (primary keys, foreign keys)
7. Design the API              (routes, request and response shapes)
8. Build, test, migrate, deploy
```

The worked example below is a shipment tracking app.

---

## Step 1 — What does the app do?

Write it in plain sentences. No code, no tables.

> - A person registers and logs in.
> - A user creates shipments and tracks their status.
> - A user can only see their own shipments.
> - Shipments can be labeled with tags like "fragile".
> - An admin can see everything.

Good questions to ask:
- Who uses it? (user, admin)
- What can each person do?
- What must never be allowed?
- What does the first version need, and what can wait?

## Step 2 — Find the entities

**Entities are the nouns**, the "things" the app stores. Underline them in your sentences:

> A **person** registers... A **user** creates **shipments**... **Shipments** can be labeled with **tags**...

| Entity | Why it exists |
|---|---|
| `User` | someone who logs in |
| `Shipment` | the main thing the app is about |
| `Tag` | a label, like "fragile" |
| `Profile` | extra personal details (optional) |

Verbs (creates, tracks, labels) usually become **routes or relationships**, not entities.

## Step 3 — List the fields

| Entity | Fields |
|---|---|
| `User` | id, email (unique), hashed_password, role |
| `Shipment` | id, content, weight, status, created_at |
| `Tag` | id, name (unique) |
| `Profile` | id, full_name, phone |

For each field ask: **Is it required? Must it be unique? What type is it?** Never store a plain password, only a hash.

## Step 4 — Find the relationships

For every pair of entities, ask two questions:
- "Can **one A** have **many B**?"
- "Can **one B** have **many A**?"

| Answers | Type | Example |
|---|---|---|
| one A → many B, each B has one A | **one-to-many** | One user has many shipments. A shipment has one owner. |
| many A ↔ many B | **many-to-many** | A shipment has many tags. A tag is on many shipments. |
| one A ↔ one B | **one-to-one** | A user has one profile. |

### How each one is stored

- **One-to-many:** the "many" side gets a **foreign key**. `shipments.owner_id` points to `users.id`.
- **One-to-one:** the same, but with a `unique` foreign key. `profiles.user_id` is unique.
- **Many-to-many:** needs a **third table** (a link or join table) that holds pairs of ids. `shipment_tags(shipment_id, tag_id)`.

## Step 5 — Draw it (ERD)

A paper sketch is enough.

```text
┌──────────┐ 1       1 ┌───────────┐
│  users   │───────────│ profiles  │
└──────────┘           └───────────┘
     │ 1
     │
     │ many
┌──────────┐ many    many ┌──────┐
│shipments │──────────────│ tags │   (through shipment_tags)
└──────────┘              └──────┘
```

Drawing it often shows a problem before you write any code, such as a missing entity or a relationship that's wrong.

## Step 6 — Turn it into tables (SQLAlchemy)

Each entity becomes a table and each relationship becomes a foreign key. I ran this code, and it creates all five tables and links them correctly:

```python
from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# many-to-many link table
shipment_tags = Table(
    "shipment_tags", Base.metadata,
    Column("shipment_id", ForeignKey("shipments.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    shipments: Mapped[list["Shipment"]] = relationship(back_populates="owner")
    profile: Mapped["Profile | None"] = relationship(back_populates="user", uselist=False)


class Profile(Base):                      # one-to-one with User
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped[User] = relationship(back_populates="profile")


class Shipment(Base):                     # many shipments belong to one user
    __tablename__ = "shipments"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(100))
    weight: Mapped[float]
    status: Mapped[str] = mapped_column(String(20), default="placed")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped[User] = relationship(back_populates="shipments")
    tags: Mapped[list["Tag"]] = relationship(secondary=shipment_tags, back_populates="shipments")


class Tag(Base):                          # many-to-many with Shipment
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    shipments: Mapped[list[Shipment]] = relationship(secondary=shipment_tags, back_populates="tags")
```

What to notice:
- Every table has a **primary key** (`id`).
- `owner_id` is the foreign key that makes one-to-many work.
- `secondary=shipment_tags` tells SQLAlchemy to use the link table for many-to-many.
- `relationship(...)` lets you write `user.shipments` and `shipment.tags` in Python without writing joins.

**Using it:**

```python
fragile = Tag(name="fragile")
amina = User(email="amina@example.com", hashed_password="x",
             profile=Profile(full_name="Amina Rahman"))
amina.shipments = [
    Shipment(content="laptop", weight=2.5, tags=[fragile]),
    Shipment(content="books", weight=4.0),
]
session.add(amina)
session.commit()

amina.profile.full_name          # "Amina Rahman"
amina.shipments[0].tags          # [fragile]
fragile.shipments                # [the laptop shipment]
```

## Step 7 — Design the API

Now the routes, based on the features from step 1:

| Feature | Route |
|---|---|
| Register | `POST /users` |
| Log in | `POST /auth/token` |
| Create a shipment | `POST /shipments` |
| List my shipments | `GET /shipments` |
| See one | `GET /shipments/{id}` |
| Change status | `PUT /shipments/{id}` |
| Tag a shipment | `POST /shipments/{id}/tags` |

For each route, decide the **path parameters**, **query parameters** and **body**, and which Pydantic models describe the input and output. Check ownership on every protected route.

## Step 8 — Build, test, migrate, deploy

1. Build one feature end to end (model, schema, route, service).
2. Test it with pytest.
3. When the tables change, add an **Alembic migration** rather than deleting the database.
4. Move from SQLite to PostgreSQL before deploying.
5. Keep secrets (database URL, JWT key) in environment variables, not in code.

---

## Design questions to ask for every table

- What identifies each row? (a primary key)
- What is required, and what can be empty?
- What must be unique?
- What should never be stored as-is? (passwords)
- Does a field repeat or hold many values? Then it probably needs its own table.
- What will I search or filter by often? That may need an index.
- What happens to related rows when one is deleted?

## Common mistakes

- Starting with code before knowing the features.
- Storing a list in one column (like `"fragile,gift"`) instead of using a link table.
- Forgetting the foreign key, so rows can point to nothing.
- Storing derived data you could calculate, like a total that can go out of sync.
- Trying to make the design perfect on the first try. Start simple and use migrations to change it.

## Practice — do these yourself

1. Pick a small app idea (a library, a blog, a to-do app). Write five sentences of what it does.
2. Underline the nouns, and list your entities and their fields.
3. For each pair of entities, decide if the relationship is one-to-many, many-to-many or one-to-one.
4. Draw the ERD on paper.
5. Write the SQLAlchemy models, using section 6 as a pattern.
6. List the routes you'd need for each feature.
